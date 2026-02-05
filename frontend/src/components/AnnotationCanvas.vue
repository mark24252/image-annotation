<script setup>
import { computed, ref, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { getAnnotations, createAnnotation, updateAnnotation, deleteAnnotation } from "../api/annotations"
import { getImage } from "../api/images"
import { predict as predictApi } from "../api/predict"
import BoundingBox from "./BoundingBox.vue"

const router = useRouter()

const props = defineProps({ imageId: String })

const container = ref(null)
const boxes = ref([])
const imageUrl = ref("")
const projectId = ref("")

const annotating = ref(false)
const predicting = ref(false)

const showClassMenu = ref(false)
const currentLabel = ref("")
const newClassName = ref("")
const pendingBox = ref(null)

const availableLabels = computed(() => {
  const set = new Set()
  for (const b of boxes.value) {
    if (b.label) set.add(b.label)
  }
  return Array.from(set)
})

const drawing = ref(false)
const start = ref({ x: 0, y: 0 })
const temp = ref(null)

const scale = ref(1)
const offset = ref({ x: 0, y: 0 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0, offsetX: 0, offsetY: 0 })

const transformStyle = computed(() => ({
  transform: `translate(${offset.value.x}px, ${offset.value.y}px) scale(${scale.value})`,
  transformOrigin: "center center"
}))

function rel(e) {
  const r = container.value?.getBoundingClientRect()
  if (!r) return { x: 0, y: 0 }
  return {
    x: Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)),
    y: Math.max(0, Math.min(1, (e.clientY - r.top) / r.height))
  }
}

// -------- Панорамирование и зум (режим просмотра) --------

function startPan(e) {
  if (annotating.value) return
  if (e.button !== 0) return
  e.preventDefault()
  isPanning.value = true
  panStart.value = {
    x: e.clientX,
    y: e.clientY,
    offsetX: offset.value.x,
    offsetY: offset.value.y
  }
  document.addEventListener("mousemove", onPanMove)
  document.addEventListener("mouseup", endPan)
}

function onPanMove(e) {
  if (!isPanning.value) return
  const dx = e.clientX - panStart.value.x
  const dy = e.clientY - panStart.value.y
  offset.value = {
    x: panStart.value.offsetX + dx,
    y: panStart.value.offsetY + dy
  }
}

function endPan() {
  if (!isPanning.value) return
  isPanning.value = false
  document.removeEventListener("mousemove", onPanMove)
  document.removeEventListener("mouseup", endPan)
}

function onWheel(e) {
  if (annotating.value) return
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  const next = Math.min(3, Math.max(0.5, scale.value + delta))
  scale.value = next
}

// -------- Рисование бокса (режим аннотации) --------

function down(e) {
  if (!annotating.value) {
    startPan(e)
    return
  }
  if (e.button !== 0) return
  const clickedBox = e.target.closest(".box")
  if (clickedBox && !clickedBox.classList.contains("box-temp")) {
    return
  }

  e.preventDefault()
  drawing.value = true
  start.value = rel(e)
  temp.value = { ...start.value, width: 0, height: 0 }
  document.addEventListener("mousemove", move)
  document.addEventListener("mouseup", up)
}

function move(e) {
  if (!drawing.value || !temp.value) return
  e.preventDefault()
  const p = rel(e)
  temp.value = {
    x: Math.min(start.value.x, p.x),
    y: Math.min(start.value.y, p.y),
    width: Math.abs(p.x - start.value.x),
    height: Math.abs(p.y - start.value.y)
  }
}

async function up(e) {
  if (e && e.button !== 0) return
  e.preventDefault()
  drawing.value = false
  document.removeEventListener("mousemove", move)
  document.removeEventListener("mouseup", up)
  if (!temp.value) return
  const { x, y, width, height } = temp.value
  if (width < 0.01 || height < 0.01) {
    temp.value = null
    return
  }
  pendingBox.value = { x, y, width, height }
  temp.value = null
  newClassName.value = ""
  currentLabel.value = ""
  showClassMenu.value = true
}

function cancelDraw() {
  drawing.value = false
  temp.value = null
  document.removeEventListener("mousemove", move)
  document.removeEventListener("mouseup", up)
}

// -------- Меню выбора класса и управление режимом аннотации --------

function startAnnotating() {
  annotating.value = true
  currentLabel.value = ""
  pendingBox.value = null
}

function cancelClassMenu() {
  showClassMenu.value = false
  pendingBox.value = null
  annotating.value = false
}

async function startAnnotationWithClass() {
  const fromExisting = currentLabel.value
  const fromNew = newClassName.value.trim()
  const label = fromNew || fromExisting
  if (!label) return
  
  if (pendingBox.value) {
    await createAnnotation(props.imageId, {
      label: label,
      x: pendingBox.value.x,
      y: pendingBox.value.y,
      width: pendingBox.value.width,
      height: pendingBox.value.height
    })
    await load()
    pendingBox.value = null
  }
  
  currentLabel.value = label
  showClassMenu.value = false
  annotating.value = false
}

function stopAnnotating() {
  annotating.value = false
  drawing.value = false
  temp.value = null
  pendingBox.value = null
}

async function load() {
  boxes.value = (await getAnnotations(props.imageId)).data
}

async function onDeleteAnnotation(annotationId) {
  await deleteAnnotation(props.imageId, annotationId)
  await load()
}

async function onEditAnnotation(box) {
  const newLabel = prompt("Новый класс", box.label)
  if (newLabel == null || newLabel === "") return
  await updateAnnotation(props.imageId, box.id, { label: newLabel })
  await load()
}

async function onUpdateAnnotation({ id, x, y, width, height }) {
  await updateAnnotation(props.imageId, id, { x, y, width, height })
  await load()
}

async function onPredict() {
  if (predicting.value) return
  predicting.value = true
  try {
    const { data } = await predictApi(props.imageId)
    const preds = data?.predictions ?? []
    for (const p of preds) {
      const [x, y, w, h] = p.bbox ?? [0, 0, 0.1, 0.1]
      await createAnnotation(props.imageId, {
        label: p.category ?? "object",
        x,
        y,
        width: w,
        height: h
      })
    }
    await load()
  } catch (err) {
    console.error("Predict failed:", err)
  } finally {
    predicting.value = false
  }
}

onMounted(async () => {
  const imageData = (await getImage(props.imageId)).data
  imageUrl.value = imageData.url
  projectId.value = imageData.project_id
  await load()
})

onUnmounted(() => {
  document.removeEventListener("mousemove", move)
  document.removeEventListener("mouseup", up)
  document.removeEventListener("mousemove", onPanMove)
  document.removeEventListener("mouseup", endPan)
})
</script>

<template>
  <div class="canvas-wrap">
    <div class="toolbar">
      <button
        v-if="projectId"
        type="button"
        class="btn-back"
        @click="() => router.push(`/projects/${projectId}`)"
      >
        ← Назад к проекту
      </button>
      
      <div class="toolbar-actions">
        <button
          type="button"
          class="btn-predict"
          :disabled="predicting"
          @click="onPredict"
        >
          {{ predicting ? "Загрузка…" : "Предсказать" }}
        </button>

        <button
          v-if="!annotating"
          type="button"
          class="btn-annotate"
          @click="startAnnotating"
        >
          Начать аннотацию
        </button>
        <button
          v-else
          type="button"
          class="btn-annotate btn-annotate--active"
          @click="stopAnnotating"
        >
          Отменить аннотацию
        </button>
      </div>
    </div>

    <div class="viewport">
    <div
      ref="container"
      class="canvas"
        :style="transformStyle"
      @mousedown="down"
      @mouseleave="cancelDraw"
        @dragstart.prevent
        @wheel.prevent="onWheel"
    >
        <img
          v-if="imageUrl"
          :src="imageUrl"
          draggable="false"
          @dragstart.prevent
        />

      <BoundingBox
        v-for="b in boxes"
        :key="b.id"
        :box="b"
        :container-ref="container"
        :disabled="drawing"
        :scale="scale"
        @delete="onDeleteAnnotation"
        @edit="onEditAnnotation"
        @update="onUpdateAnnotation"
      />

      <div
        v-if="temp"
        class="box box-temp"
        :style="{
          left: temp.x * 100 + '%',
          top: temp.y * 100 + '%',
          width: temp.width * 100 + '%',
          height: temp.height * 100 + '%'
        }"
      />
      </div>
    </div>

    <div v-if="showClassMenu" class="label-form-overlay" @click.self="cancelClassMenu">
      <div class="label-form">
        <label>Выберите класс аннотации</label>
        <select
          v-if="availableLabels.length"
          v-model="currentLabel"
          class="label-select"
        >
          <option disabled value="">Выберите существующий класс</option>
          <option v-for="lbl in availableLabels" :key="lbl" :value="lbl">
            {{ lbl }}
          </option>
        </select>

        <label>Или добавьте новый класс</label>
        <input
          v-model="newClassName"
          type="text"
          placeholder="Новый класс"
        />

        <div class="label-form__actions">
          <button type="button" @click="cancelClassMenu">Отмена</button>
          <button type="button" @click="startAnnotationWithClass">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.canvas-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
}

.canvas {
  position: relative;
  display: inline-block;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.canvas img {
  user-select: none;
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  user-drag: none;
}

.toolbar {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-back {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  color: #213547;
}

.btn-back:hover {
  background-color: #e9e9e9;
  border-color: #bbb;
}

.btn-predict {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #007bff;
  background: #007bff;
  color: white;
  cursor: pointer;
  font-weight: 500;
}

.btn-predict:hover:not(:disabled) {
  background: #0056b3;
  border-color: #0056b3;
}

.btn-predict:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-annotate {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #28a745;
  background: #28a745;
  color: white;
  cursor: pointer;
  font-weight: 500;
}

.btn-annotate--active {
  background: #218838;
  border-color: #1e7e34;
}

.viewport {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  overflow: hidden;
}

.box-temp {
  position: absolute;
  border: 2px solid red;
  pointer-events: none;
}

.label-form-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.label-form {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  min-width: 260px;
}

.label-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.label-form input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 12px;
  box-sizing: border-box;
}

.label-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 12px;
  box-sizing: border-box;
}

.label-form__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.label-form__actions button {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
  background: #f5f5f5;
  cursor: pointer;
}

.label-form__actions button:last-child {
  background: #007bff;
  color: white;
  border-color: #007bff;
}
</style>
