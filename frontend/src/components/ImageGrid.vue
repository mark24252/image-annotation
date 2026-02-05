<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from "vue"
import { useImagesStore } from "../store/images"
import { deleteImage } from "../api/images"

const props = defineProps({
  projectId: String
})

const store = useImagesStore()

const images = ref([])
const selectedImages = ref(new Set())
const isDeleting = ref(false)

const hasSelection = computed(() => selectedImages.value.size > 0)

function updateImages() {
  images.value = store.images(props.projectId) || []
  selectedImages.value.clear()
}

let unsubscribe = null

onMounted(() => {
  unsubscribe = store.$subscribe((mutation, state) => {
    updateImages()
  })
  
  if (props.projectId) {
    store.load(props.projectId).then(() => {
      updateImages()
    })
  }
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
})

watch(() => props.projectId, (newProjectId, oldProjectId) => {
  if (newProjectId) {
    if (oldProjectId && oldProjectId !== newProjectId) {
      images.value = []
      selectedImages.value.clear()
      store.$patch((state) => {
        state.imagesByProject[oldProjectId] = []
      })
    }
    store.load(newProjectId).then(() => {
      updateImages()
    })
  }
}, { immediate: true })

function toggleSelection(imageId) {
  if (selectedImages.value.has(imageId)) {
    selectedImages.value.delete(imageId)
  } else {
    selectedImages.value.add(imageId)
  }
}

function selectAll() {
  images.value.forEach(img => selectedImages.value.add(img.id))
}

function deselectAll() {
  selectedImages.value.clear()
}

async function deleteSelected() {
  if (!hasSelection.value || isDeleting.value) return
  
  if (!confirm(`Удалить ${selectedImages.value.size} изображений?`)) {
    return
  }
  
  isDeleting.value = true
  const idsToDelete = Array.from(selectedImages.value)
  
  try {
    await Promise.all(idsToDelete.map(id => deleteImage(id)))
    selectedImages.value.clear()
    await store.load(props.projectId)
    updateImages()
  } catch (error) {
    console.error("Ошибка при удалении изображений:", error)
    alert("Произошла ошибка при удалении изображений")
  } finally {
    isDeleting.value = false
  }
}

function onImageClick(e, imageId) {
  if (e.ctrlKey || e.metaKey || e.shiftKey) {
    e.preventDefault()
    toggleSelection(imageId)
  }
}
</script>

<template>
  <div class="images-section">
    <div v-if="images.length > 0" class="images-toolbar">
      <div class="selection-info">
        <span v-if="hasSelection">
          Выбрано: {{ selectedImages.size }} из {{ images.length }}
        </span>
        <span v-else class="hint">Используйте Ctrl+Click для выбора изображений</span>
      </div>
      <div class="toolbar-actions">
        <button 
          v-if="!hasSelection" 
          @click="selectAll" 
          class="btn-select-all"
        >
          Выбрать все
        </button>
        <button 
          v-if="hasSelection" 
          @click="deselectAll" 
          class="btn-deselect"
        >
          Снять выбор
        </button>
        <button 
          v-if="hasSelection" 
          @click="deleteSelected" 
          class="btn-delete-selected"
          :disabled="isDeleting"
        >
          {{ isDeleting ? "Удаление..." : `Удалить выбранные (${selectedImages.size})` }}
        </button>
      </div>
    </div>

    <div class="image-grid">
      <div
        v-for="img in images"
        :key="img.id"
        class="image-item"
        :class="{ 'image-item--selected': selectedImages.has(img.id) }"
        @click="onImageClick($event, img.id)"
      >
        <div class="image-checkbox">
          <input
            type="checkbox"
            :checked="selectedImages.has(img.id)"
            @change="toggleSelection(img.id)"
            @click.stop
          />
        </div>
        <router-link 
          :to="`/images/${img.id}`" 
          class="image-link"
          @click="(e) => { if (e.ctrlKey || e.metaKey || e.shiftKey) e.preventDefault() }"
        >
          <img
            :src="img.url"
            class="image-thumb"
            alt=""
          />
        </router-link>
      </div>
    </div>
    
    <div v-if="!store.loading && !images.length" class="no-images">
      Нет изображений в этом проекте
    </div>
  </div>
</template>

<style scoped>
.images-section {
  margin-top: 24px;
}

.images-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 12px;
}

.selection-info {
  color: #666;
  font-size: 14px;
}

.selection-info .hint {
  color: #999;
  font-style: italic;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-select-all,
.btn-deselect {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-select-all:hover,
.btn-deselect:hover {
  background-color: #e0e0e0;
}

.btn-delete-selected {
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-delete-selected:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-delete-selected:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.image-item {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  border: 2px solid transparent;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.image-item:hover {
  border-color: #646cff;
  box-shadow: 0 2px 8px rgba(100, 108, 255, 0.2);
}

.image-item--selected {
  border-color: #646cff;
  box-shadow: 0 0 0 3px rgba(100, 108, 255, 0.3);
}

.image-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 4px;
}

.image-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.image-link {
  display: block;
  width: 100%;
  height: 100%;
}

.image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 6px;
}

.no-images {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

@media (max-width: 768px) {
  .images-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-actions {
    width: 100%;
  }
  
  .btn-select-all,
  .btn-deselect,
  .btn-delete-selected {
    flex: 1;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 8px;
  }
}
</style>