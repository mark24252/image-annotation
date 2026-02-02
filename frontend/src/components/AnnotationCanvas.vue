<script setup>
import { ref, onMounted } from "vue"
import { getAnnotations, createAnnotation, updateAnnotation, deleteAnnotation } from "../api/annotations"
import { getImage } from "../api/images"
import BoundingBox from "./BoundingBox.vue"

const props = defineProps({ imageId: String })

const container = ref(null)
const boxes = ref([])
const imageUrl = ref("")
const drawing = ref(false)
const start = ref({ x: 0, y: 0 })
const temp = ref(null)
const showLabelForm = ref(false)
const pendingBox = ref(null)
const labelInput = ref("")

function rel(e) {
  const r = container.value.getBoundingClientRect()
  return {
    x: (e.clientX - r.left) / r.width,
    y: (e.clientY - r.top) / r.height
  }
}

function down(e) {
  drawing.value = true
  start.value = rel(e)
  temp.value = { ...start.value, width: 0, height: 0 }
}

function move(e) {
  if (!drawing.value) return
  const p = rel(e)
  temp.value.width = p.x - start.value.x
  temp.value.height = p.y - start.value.y
}

function up() {
  drawing.value = false
  if (!temp.value) return
  pendingBox.value = { ...temp.value }
  temp.value = null
  labelInput.value = ""
  showLabelForm.value = true
}

async function submitLabelForm() {
  const label = labelInput.value.trim()
  if (!label || !pendingBox.value) return
  await createAnnotation(props.imageId, {
    label,
    x: pendingBox.value.x,
    y: pendingBox.value.y,
    width: pendingBox.value.width,
    height: pendingBox.value.height
  })
  showLabelForm.value = false
  pendingBox.value = null
  await load()
}

function cancelLabelForm() {
  showLabelForm.value = false
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

onMounted(async () => {
  imageUrl.value = (await getImage(props.imageId)).data.url
  await load()
})
</script>

<template>
  <div class="canvas-wrap">
    <div
      ref="container"
      class="canvas"
      @mousedown="down"
      @mousemove="move"
      @mouseup="up"
    >
      <img v-if="imageUrl" :src="imageUrl" />

      <BoundingBox
        v-for="b in boxes"
        :key="b.id"
        :box="b"
        @delete="onDeleteAnnotation"
        @edit="onEditAnnotation"
      />

      <div
        v-if="temp"
        class="box"
        :style="{
          left: temp.x * 100 + '%',
          top: temp.y * 100 + '%',
          width: temp.width * 100 + '%',
          height: temp.height * 100 + '%'
        }"
      />
    </div>

    <div v-if="showLabelForm" class="label-form-overlay" @click.self="cancelLabelForm">
      <div class="label-form">
        <label for="label-input">Класс (метка)</label>
        <input
          id="label-input"
          v-model="labelInput"
          type="text"
          placeholder="Введите класс"
          autofocus
          @keydown.enter="submitLabelForm"
          @keydown.esc="cancelLabelForm"
        />
        <div class="label-form__actions">
          <button type="button" @click="cancelLabelForm">Отмена</button>
          <button type="button" @click="submitLabelForm">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.canvas-wrap {
  position: relative;
  display: inline-block;
}

.canvas {
  position: relative;
  display: inline-block;
}

.box {
  position: absolute;
  border: 2px solid red;
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
