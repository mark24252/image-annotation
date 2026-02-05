import api from "./client"

export const getProjects = () => api.get("/projects")
export const getProject = (id) => api.get(`/projects/${id}`)
export const createProject = (name) =>
  api.post("/projects", { name })
export const deleteProject = (id) =>
  api.delete(`/projects/${id}`)
