<script setup>
import { ref, onMounted } from "vue"
import { useProjectsStore } from "../store/projects"

const store = useProjectsStore()
const name = ref("")

onMounted(() => store.load())

function add() {
  if (!name.value) return
  store.add(name.value)
  name.value = ""
}
</script>

<template>
  <h1>Projects</h1>

  <input v-model="name" placeholder="Project name" />
  <button @click="add">Create</button>

  <ul>
    <li v-for="p in store.projects" :key="p.id">
      <router-link :to="`/projects/${p.id}`">
        {{ p.name }}
      </router-link>
      <button @click="store.remove(p.id)">❌</button>
    </li>
  </ul>
</template>
