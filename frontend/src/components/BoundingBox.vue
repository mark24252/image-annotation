<script setup>
import { computed, ref, watch, onUnmounted } from "vue"

const props = defineProps({
  box: Object,
  containerRef: Object,
  disabled: Boolean,
  scale: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(["delete", "edit", "update"])

const menuVisible = ref(false)
const menuX = ref(0)
const menuY = ref(0)
const menuRef = ref(null)
const boxRef = ref(null)

const MODE_NONE = "none"
const MODE_MOVE = "move"
const MODE_RESIZE = "resize"

const mode = ref(MODE_NONE)
const resizeHandle = ref(null)
const moveStart = ref({ x: 0, y: 0, boxX: 0, boxY: 0, boxW: 0, boxH: 0 })
const draft = ref(null)

const tooltipText = computed(() => {
  if (!props.box) return ""
  const b = props.box
  const coords = `x: ${(b.x ?? 0).toFixed(3)}, y: ${(b.y ?? 0).toFixed(3)}`
  const dims = `w: ${(b.width ?? 0).toFixed(3)}, h: ${(b.height ?? 0).toFixed(3)}`
  return `Класс: ${b.label ?? ""}\nКоординаты: ${coords}\nРазмеры: ${dims}`
})

const boxStyle = computed(() => {
  const b = draft.value ?? props.box
  const x = (b.x ?? 0) * 100
  const y = (b.y ?? 0) * 100
  const w = Math.max(0, (b.width ?? 0) * 100)
  const h = Math.max(0, (b.height ?? 0) * 100)
  const invScale = 1 / (props.scale || 1)
  return {
    left: x + "%",
    top: y + "%",
    width: w + "%",
    height: h + "%",
    pointerEvents: props.disabled ? "none" : "auto",
    "--bb-inv-scale": invScale
  }
})

function rel(e) {
  const r = props.containerRef?.getBoundingClientRect()
  if (!r) return { x: 0, y: 0 }
  return {
    x: Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)),
    y: Math.max(0, Math.min(1, (e.clientY - r.top) / r.height))
  }
}

function onMoveStart(e) {
  if (e.button !== 0 || props.disabled) return
  e.preventDefault()
  e.stopPropagation()
  const p = rel(e)
  mode.value = MODE_MOVE
  moveStart.value = {
    x: p.x,
    y: p.y,
    boxX: props.box.x,
    boxY: props.box.y,
    boxW: props.box.width,
    boxH: props.box.height
  }
  document.addEventListener("mousemove", onMoveMove)
  document.addEventListener("mouseup", onMoveUp)
}

function onMoveMove(e) {
  if (mode.value !== MODE_MOVE) return
  const p = rel(e)
  const dx = p.x - moveStart.value.x
  const dy = p.y - moveStart.value.y
  let nx = moveStart.value.boxX + dx
  let ny = moveStart.value.boxY + dy
  nx = Math.max(0, Math.min(1 - moveStart.value.boxW, nx))
  ny = Math.max(0, Math.min(1 - moveStart.value.boxH, ny))
  draft.value = {
    ...props.box,
    x: nx,
    y: ny,
    width: moveStart.value.boxW,
    height: moveStart.value.boxH
  }
}

function onMoveUp() {
  if (mode.value === MODE_MOVE) {
    if (draft.value) {
      emit("update", {
        id: props.box.id,
        x: draft.value.x,
        y: draft.value.y,
        width: draft.value.width,
        height: draft.value.height
      })
      draft.value = null
    }
    mode.value = MODE_NONE
    document.removeEventListener("mousemove", onMoveMove)
    document.removeEventListener("mouseup", onMoveUp)
  }
}

function onResizeStart(e, handle) {
  if (e.button !== 0 || props.disabled) return
  e.preventDefault()
  e.stopPropagation()
  mode.value = MODE_RESIZE
  resizeHandle.value = handle
  moveStart.value = {
    x: rel(e).x,
    y: rel(e).y,
    boxX: props.box.x,
    boxY: props.box.y,
    boxW: props.box.width,
    boxH: props.box.height
  }
  document.addEventListener("mousemove", onResizeMove)
  document.addEventListener("mouseup", onResizeUp)
}

function onResizeMove(e) {
  if (mode.value !== MODE_RESIZE || !resizeHandle.value) return
  const p = rel(e)
  const h = resizeHandle.value
  let x = moveStart.value.boxX
  let y = moveStart.value.boxY
  let w = moveStart.value.boxW
  let hh = moveStart.value.boxH

  const minSize = 0.02

  if (h.includes("e")) {
    w = Math.max(minSize, p.x - x)
    w = Math.min(w, 1 - x)
  }
  if (h.includes("w")) {
    const newX = Math.min(p.x, x + w - minSize)
    w = x + w - newX
    x = newX
  }
  if (h.includes("s")) {
    hh = Math.max(minSize, p.y - y)
    hh = Math.min(hh, 1 - y)
  }
  if (h.includes("n")) {
    const newY = Math.min(p.y, y + hh - minSize)
    hh = y + hh - newY
    y = newY
  }

  x = Math.max(0, Math.min(1 - minSize, x))
  y = Math.max(0, Math.min(1 - minSize, y))
  w = Math.max(minSize, Math.min(1 - x, w))
  hh = Math.max(minSize, Math.min(1 - y, hh))

  draft.value = { ...props.box, x, y, width: w, height: hh }
}

function onResizeUp() {
  if (mode.value === MODE_RESIZE) {
    if (draft.value) {
      emit("update", {
        id: props.box.id,
        x: draft.value.x,
        y: draft.value.y,
        width: draft.value.width,
        height: draft.value.height
      })
      draft.value = null
    }
    mode.value = MODE_NONE
    resizeHandle.value = null
    document.removeEventListener("mousemove", onResizeMove)
    document.removeEventListener("mouseup", onResizeUp)
  }
}

function onContextMenu(e) {
  e.preventDefault()
  e.stopPropagation()
  
  if (boxRef.value && props.containerRef) {
    const boxX = (props.box.x ?? 0) * 100
    const boxY = (props.box.y ?? 0) * 100
    const boxW = (props.box.width ?? 0) * 100
    const boxH = (props.box.height ?? 0) * 100
    
    menuX.value = boxX + boxW / 2
    menuY.value = boxY + boxH / 2
  } else {
    const containerRect = props.containerRef?.getBoundingClientRect()
    if (containerRect) {
      const relX = ((e.clientX - containerRect.left) / containerRect.width) * 100
      const relY = ((e.clientY - containerRect.top) / containerRect.height) * 100
      menuX.value = relX
      menuY.value = relY
    } else {
      menuX.value = 50
      menuY.value = 50
    }
  }
  
  menuVisible.value = true
}

function closeMenu() {
  menuVisible.value = false
  document.removeEventListener("click", onDocumentClick)
}

function onDocumentClick(e) {
  if (menuRef.value && menuRef.value.contains(e.target)) {
    return
  }
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

watch(
  () => props.box,
  () => {
    if (mode.value === MODE_NONE) draft.value = null
  },
  { deep: true }
)

watch(menuVisible, (visible) => {
  if (visible) {
    setTimeout(() => document.addEventListener("click", onDocumentClick), 0)
  }
})

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick)
  document.removeEventListener("mousemove", onMoveMove)
  document.removeEventListener("mouseup", onMoveUp)
  document.removeEventListener("mousemove", onResizeMove)
  document.removeEventListener("mouseup", onResizeUp)
})
</script>

<template>
  <div
    ref="boxRef"
    class="box"
    :style="boxStyle"
    :title="tooltipText"
    @contextmenu="onContextMenu"
    @mousedown="onMoveStart"
  >
    <div class="box-fill" />
    <div class="handle handle-n" @mousedown="onResizeStart($event, 'n')" />
    <div class="handle handle-ne" @mousedown="onResizeStart($event, 'ne')" />
    <div class="handle handle-e" @mousedown="onResizeStart($event, 'e')" />
    <div class="handle handle-se" @mousedown="onResizeStart($event, 'se')" />
    <div class="handle handle-s" @mousedown="onResizeStart($event, 's')" />
    <div class="handle handle-sw" @mousedown="onResizeStart($event, 'sw')" />
    <div class="handle handle-w" @mousedown="onResizeStart($event, 'w')" />
    <div class="handle handle-nw" @mousedown="onResizeStart($event, 'nw')" />

    <div
      v-if="menuVisible"
      ref="menuRef"
      class="context-menu"
      :style="{ left: menuX + '%', top: menuY + '%', transform: 'translate(-50%, -50%)' }"
      @click.stop
      @mousedown.stop
    >
      <button type="button" @click.stop="onEdit">Изменить класс</button>
      <button type="button" @click.stop="onDelete">Удалить</button>
    </div>
  </div>
</template>

<style scoped>
.box {
  position: absolute;
  border: 2px solid red;
  cursor: default;
  box-sizing: border-box;
}

.box-fill {
  position: absolute;
  inset: 2px;
  background: rgba(255, 0, 0, 0.25);
  cursor: move;
  border-radius: 1px;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.15s, visibility 0s 0.15s;
  pointer-events: none !important;
}

.box:hover .box-fill {
  visibility: visible;
  opacity: 1;
  transition: opacity 0.15s;
  pointer-events: none !important;
}

.handle {
  position: absolute;
  width: calc(10px * var(--bb-inv-scale, 1));
  height: calc(10px * var(--bb-inv-scale, 1));
  margin: calc(-5px * var(--bb-inv-scale, 1));
  background: rgba(0, 255, 0, 0.8);
  border: 1px solid #000;
  cursor: nwse-resize;
  z-index: 2;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.15s, visibility 0s 0.15s;
  pointer-events: none;
}

.box:hover .handle {
  visibility: visible;
  opacity: 1;
  transition: opacity 0.15s;
  pointer-events: auto;
}

.handle-n {
  top: 0;
  left: 50%;
  margin-left: calc(-5px * var(--bb-inv-scale, 1));
  cursor: ns-resize;
}
.handle-s {
  bottom: 0;
  left: 50%;
  margin-left: calc(-5px * var(--bb-inv-scale, 1));
  cursor: ns-resize;
}
.handle-e {
  right: 0;
  top: 50%;
  margin-top: calc(-5px * var(--bb-inv-scale, 1));
  cursor: ew-resize;
}
.handle-w {
  left: 0;
  top: 50%;
  margin-top: calc(-5px * var(--bb-inv-scale, 1));
  cursor: ew-resize;
}
.handle-ne {
  top: 0;
  right: 0;
  cursor: nesw-resize;
}
.handle-nw {
  top: 0;
  left: 0;
  cursor: nwse-resize;
}
.handle-se {
  bottom: 0;
  right: 0;
  cursor: nwse-resize;
}
.handle-sw {
  bottom: 0;
  left: 0;
  cursor: nesw-resize;
}

.context-menu {
  position: absolute;
  z-index: 1000;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  min-width: 140px;
  pointer-events: auto;
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