import { createRouter, createWebHistory } from "vue-router"
import ProjectsView from "../views/ProjectsView.vue"
import ProjectDetailView from "../views/ProjectDetailView.vue"
import AnnotateView from "../views/AnnotateView.vue"

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: ProjectsView },
    { path: "/projects/:id", component: ProjectDetailView },
    { path: "/images/:id", component: AnnotateView }
  ]
})