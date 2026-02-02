import api from "./client"

export const uploadImages = (projectId, files) => {
  const form = new FormData()
  files.forEach(f => form.append("files", f))
  return api.post(`/projects/${projectId}/images`, form)
}

export const getImages = (projectId) =>
  api.get(`/projects/${projectId}/images`)

export const getImage = (id) =>
  api.get(`/images/${id}`)

export const deleteImage = (id) =>
  api.delete(`/images/${id}`)
