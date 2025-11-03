import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Index from '@/views/Index.vue';
import Dataset from '@/views/Dataset.vue';
import ModelEvaluation from '@/views/ModelEvaluation.vue';
import Login from '@/views/Login.vue';

const routes = [
    {path: "/", component: Index },
    {path: '/dashboard', component: Dashboard},
    {path: '/dashboard/datasets', component: Dataset},
    {path: '/dashboard/modelevaluation', component: ModelEvaluation},
    {path: '/login', component: Login},
    {path: '/register', component: Register},

];

const router = createRouter({
    history: createWebHistory(),
    routes
});


router.beforeEach((to, from, next) => {
    const publicPaths = ["/login", "/register", "/"];
    if (!publicPaths.includes(to.path) && !token) {
    next("/login");
    } else {
    next();
    }
});



export default router;
