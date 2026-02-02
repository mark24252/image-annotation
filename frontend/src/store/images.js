import { defineStore } from "pinia"
import { getImages, uploadImages, deleteImage } from "../api/images"

export const useImagesStore = defineStore("images", {
  state: () => ({
    images: [],
    loading: false
  }),

  actions: {
    async load(projectId) {
      this.loading = true
      this.images = (await getImages(projectId)).data
      this.loading = false
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
