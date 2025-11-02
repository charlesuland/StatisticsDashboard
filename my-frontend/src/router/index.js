import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard.vue';
import Index from '@/views/Index.vue';
import Dataset from '@/views/Dataset.vue';

const routes = [
    {path: "/", component: Index },
    {path: '/dashboard', component: Dashboard},
    {path: '/dashboard/datasets', component: Dataset},
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
