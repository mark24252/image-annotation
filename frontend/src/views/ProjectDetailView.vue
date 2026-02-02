<script setup>
import { useRoute } from "vue-router"
import ImageUploader from "../components/ImageUploader.vue"
import ImageGrid from "../components/ImageGrid.vue"
import { useImagesStore } from "../store/images"

const route = useRoute()
const imagesStore = useImagesStore()

function onUploaded() {
  imagesStore.load(route.params.id)
}
</script>

<template>
  <h2>Images</h2>

  <ImageUploader :projectId="route.params.id" @uploaded="onUploaded" />
  <ImageGrid :projectId="route.params.id" />
</template>
