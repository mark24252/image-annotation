<script setup>
import { useRoute } from "vue-router"
import AnnotationCanvas from "../components/AnnotationCanvas.vue"

const route = useRoute()
</script>

<template>
  <AnnotationCanvas :imageId="route.params.id" />
</template>