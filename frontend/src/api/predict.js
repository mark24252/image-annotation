import api from "./client"

export const predict = (imageId) =>
  api.post(`/predict/${imageId}`)