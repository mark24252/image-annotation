import { defineStore } from "pinia"
import { getProjects, createProject, deleteProject } from "../api/projects"

export const useProjectsStore = defineStore("projects", {
  state: () => ({
    projects: [],
    loading: false
  }),

  actions: {
    async load() {
      this.loading = true
      this.projects = (await getProjects()).data
      this.loading = false
    },

    async add(name) {
      await createProject(name)
      await this.load()
    },

    async remove(id) {
      await deleteProject(id)
      await this.load()
    }
  }
})
