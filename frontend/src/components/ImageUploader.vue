<script setup>
import { ref } from "vue"
import { uploadImages } from "../api/images"

const props = defineProps({ projectId: String })
const emit = defineEmits(["uploaded"])

const fileInput = ref(null)
const dragOver = ref(false)

async function onChange(e) {
  const files = e.target.files
  if (!files?.length) return
  await uploadImages(props.projectId, [...files])
  emit("uploaded")
  e.target.value = ""
}

function onDragOver(e) {
  e.preventDefault()
  e.stopPropagation()
  dragOver.value = true
}

function onDragLeave(e) {
  e.preventDefault()
  e.stopPropagation()
  dragOver.value = false
}

async function onDrop(e) {
  e.preventDefault()
  e.stopPropagation()
  dragOver.value = false
  const files = [...(e.dataTransfer?.files ?? [])].filter(
    (f) => f.type.startsWith("image/")
  )
  if (!files.length) return
  await uploadImages(props.projectId, files)
  emit("uploaded")
}

function onZoneClick() {
  fileInput.value?.click()
}
</script>

<template>
  <div
    class="drop-zone"
    :class="{ 'drop-zone--over': dragOver }"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
    @click="onZoneClick"
  >
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      multiple
      class="drop-zone__input"
      @change="onChange"
    />
    <span class="drop-zone__text">
      Перетащите изображения сюда или нажмите для выбора
    </span>
  </div>
</template>

<style scoped>
.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.drop-zone:hover,
.drop-zone--over {
  border-color: #888;
  background: #f8f8f8;
}

.drop-zone__input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.drop-zone__text {
  color: #666;
}
</style>
