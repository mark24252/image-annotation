import { defineStore } from "pinia"
import { getImages, uploadImages, deleteImage } from "../api/images"

export const useImagesStore = defineStore("images", {
  state: () => ({
    imagesByProject: {},
    loading: false
  }),

  getters: {
    images: (state) => (projectId) => {
      return state.imagesByProject[projectId] || []
    }
  },

  actions: {
    async load(projectId) {
      if (!projectId) return
      
      this.loading = true
      try {
        const response = await getImages(projectId)
        this.$patch((state) => {
          state.imagesByProject[projectId] = response.data
        })
      } finally {
        this.loading = false
      }
    },

    async upload(projectId, files) {
      await uploadImages(projectId, files)
      await this.load(projectId)
    },

    async remove(imageId, projectId) {
      await deleteImage(imageId)
      await this.load(projectId)
    }
  }
})