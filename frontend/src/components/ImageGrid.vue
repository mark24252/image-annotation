<script setup>
import { onMounted } from "vue"
import { useImagesStore } from "../store/images"

const props = defineProps({
  projectId: String
})

const store = useImagesStore()

onMounted(() => store.load(props.projectId))
</script>

<template>
  <div style="display:flex;gap:10px;flex-wrap:wrap">
    <div v-for="img in store.images" :key="img.id">
      <router-link :to="`/images/${img.id}`">
        <img
          :src="img.url"
          width="150"
        />
      </router-link>
    </div>
  </div>
</template>
