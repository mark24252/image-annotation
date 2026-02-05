<script setup>
import { ref, onMounted } from "vue"
import { useProjectsStore } from "../store/projects"

const store = useProjectsStore()
const name = ref("")

onMounted(() => store.load())

function add() {
  if (!name.value.trim()) return
  store.add(name.value.trim())
  name.value = ""
}
</script>

<template>
  <div class="projects-page">
    <div class="projects-header">
      <h1>Проекты</h1>
      <div class="create-project-form">
        <input 
          v-model="name" 
          placeholder="Название проекта" 
          @keyup.enter="add"
          class="project-input"
        />
        <button @click="add" class="btn-create">Создать проект</button>
      </div>
    </div>

    <div v-if="store.loading" class="loading">Загрузка...</div>
    
    <div v-else-if="store.projects.length === 0" class="empty-state">
      <p>Нет проектов. Создайте первый проект!</p>
    </div>

    <div v-else class="projects-grid">
      <div 
        v-for="p in store.projects" 
        :key="p.id"
        class="project-card"
      >
        <router-link :to="`/projects/${p.id}`" class="project-card__link">
          <div class="project-card__icon">📁</div>
          <h3 class="project-card__name">{{ p.name }}</h3>
        </router-link>
        <button 
          @click.stop="store.remove(p.id)" 
          class="project-card__delete"
          title="Удалить проект"
        >
          🗑️
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.projects-header {
  margin-bottom: 32px;
}

.projects-header h1 {
  font-size: 2.5em;
  margin-bottom: 24px;
  color: #213547;
}

.create-project-form {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.project-input {
  flex: 1;
  min-width: 200px;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

.project-input:focus {
  outline: none;
  border-color: #646cff;
}

.btn-create {
  padding: 12px 24px;
  background-color: #646cff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-create:hover {
  background-color: #535bf2;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 18px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 18px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.project-card {
  position: relative;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.project-card:hover {
  border-color: #646cff;
  box-shadow: 0 4px 12px rgba(100, 108, 255, 0.15);
  transform: translateY(-2px);
}

.project-card__link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.project-card__icon {
  font-size: 48px;
  margin-bottom: 12px;
  text-align: center;
}

.project-card__name {
  margin: 0;
  font-size: 1.2em;
  color: #213547;
  text-align: center;
  word-break: break-word;
}

.project-card__delete {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
  opacity: 0.6;
}

.project-card__delete:hover {
  opacity: 1;
  background-color: #fee;
}

@media (max-width: 768px) {
  .projects-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .projects-header h1 {
    font-size: 2em;
  }
  
  .create-project-form {
    flex-direction: column;
  }
  
  .project-input {
    width: 100%;
  }
  
  .btn-create {
    width: 100%;
  }
}
</style>
