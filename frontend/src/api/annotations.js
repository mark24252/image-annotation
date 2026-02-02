import api from "./client"

export const getAnnotations = (imageId) =>
  api.get(`/images/${imageId}/annotations`)

export const createAnnotation = (imageId, data) =>
  api.post(`/images/${imageId}/annotations`, data)

export const updateAnnotation = (imageId, annotationId, data) =>
  api.patch(`/images/${imageId}/annotations/${annotationId}`, data)

export const deleteAnnotation = (imageId, annotationId) =>
  api.delete(`/images/${imageId}/annotations/${annotationId}`)