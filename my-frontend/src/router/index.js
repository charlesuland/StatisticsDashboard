import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Index from '@/views/Index.vue';
import Dataset from '@/views/Dataset.vue';
import ModelEvaluation from '@/views/ModelEvaluation.vue';

const routes = [
    {path: "/", component: Index },
    {path: '/dashboard', component: Dashboard},
    {path: '/dashboard/datasets', component: Dataset},
    {path: '/dashboard/modelevaluation', component: ModelEvaluation},
    
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
