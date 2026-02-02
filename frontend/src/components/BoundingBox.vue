<script setup>
import { computed, ref, watch, onUnmounted } from "vue"

const props = defineProps({ box: Object })
const emit = defineEmits(["delete", "edit"])

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)

const tooltipText = computed(() => {
  if (!props.box) return ""
  const b = props.box
  const coords = `x: ${(b.x ?? 0).toFixed(3)}, y: ${(b.y ?? 0).toFixed(3)}`
  const dims = `w: ${(b.width ?? 0).toFixed(3)}, h: ${(b.height ?? 0).toFixed(3)}`
  return `Класс: ${b.label ?? ""}\nКоординаты: ${coords}\nРазмеры: ${dims}`
})

function onContextMenu(e) {
  e.preventDefault()
  e.stopPropagation()
  menuX.value = e.clientX
  menuY.value = e.clientY
  menuVisible.value = true
}

function closeMenu() {
  menuVisible.value = false
  document.removeEventListener("click", onDocumentClick)
}

function onDocumentClick() {
  closeMenu()
}

function onDelete() {
  emit("delete", props.box.id)
  closeMenu()
}

function onEdit() {
  emit("edit", props.box)
  closeMenu()
}

watch(menuVisible, (visible) => {
  if (visible) {
    setTimeout(() => document.addEventListener("click", onDocumentClick), 0)
  }
})

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick)
})
</script>

<template>
  <div
    class="box"
    :style="{
      left: box.x * 100 + '%',
      top: box.y * 100 + '%',
      width: box.width * 100 + '%',
      height: box.height * 100 + '%'
    }"
    :title="tooltipText"
    @contextmenu="onContextMenu"
    @mousedown.stop
    @mouseup.stop
    @mousemove.stop
  >
    <div
      v-if="menuVisible"
      class="context-menu"
      :style="{ left: menuX + 'px', top: menuY + 'px' }"
      @click.stop
    >
      <button type="button" @click="onEdit">Изменить класс</button>
      <button type="button" @click="onDelete">Удалить</button>
    </div>
  </div>
</template>

<style scoped>
.box {
  position: absolute;
  border: 2px solid lime;
  cursor: context-menu;
}

.context-menu {
  position: fixed;
  z-index: 1000;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  min-width: 140px;
}

.context-menu button {
  display: block;
  width: 100%;
  padding: 6px 12px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
}

.context-menu button:hover {
  background: #f0f0f0;
}
</style>