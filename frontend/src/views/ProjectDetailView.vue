<script setup>
import { useRoute, useRouter } from "vue-router"
import { ref, onMounted } from "vue"
import ImageUploader from "../components/ImageUploader.vue"
import ImageGrid from "../components/ImageGrid.vue"
import { useImagesStore } from "../store/images"
import { getProject } from "../api/projects"

const route = useRoute()
const router = useRouter()
const imagesStore = useImagesStore()
const projectName = ref("")

onMounted(async () => {
  try {
    const project = (await getProject(route.params.id)).data
    projectName.value = project.name
  } catch (err) {
    console.error("Failed to load project:", err)
  }
})

function onUploaded() {
  imagesStore.load(route.params.id)
}

function goBack() {
  router.push("/")
}
</script>

<template>
  <div class="project-detail-page">
    <div class="page-header">
      <button @click="goBack" class="btn-back">← Назад к проектам</button>
      <h2>{{ projectName || "Проект" }}</h2>
    </div>

    <div class="content-section">
      <ImageUploader :projectId="route.params.id" @uploaded="onUploaded" />
    </div>

    <ImageGrid :projectId="route.params.id" />
  </div>
</template>

<style scoped>
.project-detail-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.btn-back {
  margin-bottom: 16px;
  padding: 10px 20px;
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

.page-header h2 {
  font-size: 2em;
  margin: 0;
  color: #213547;
}

.content-section {
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .project-detail-page {
    padding: 16px;
  }
  
  .page-header h2 {
    font-size: 1.5em;
  }
}
</style>