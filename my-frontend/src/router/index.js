import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Index from '@/views/Index.vue';
import Dataset from '@/views/Dataset.vue';
import ModelEvaluation from '@/views/ModelEvaluation.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import CompareModels from '@/views/CompareModels.vue';

const routes = [
    {path: "/", component: Index },
    {path: '/dashboard', component: Dashboard},
    {path: '/dashboard/datasets', component: Dataset},
    {path: '/dashboard/modelevaluation', component: ModelEvaluation},
    {path: '/login', component: Login},
    {path: '/register', component: Register},
    {path: '/dashboard/comparemodels', component: CompareModels},

];

const router = createRouter({
    history: createWebHistory(),
    routes
});


router.beforeEach((to, from, next) => {
    const publicPaths = ["/login", "/register", "/"];
    const token = localStorage.getItem("token"); // must come before if-statement!
    if (!publicPaths.includes(to.path) && !token) {
    next("/login");
    } else {
    next();
    }
});



export default router;
