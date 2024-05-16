<script setup>
import { useRoute } from 'vue-router';


const route = useRoute();
const exam_name = JSON.parse(atob(route.params.info)).name;
const exam_token = JSON.parse(atob(route.params.info)).auth_token;

</script>
<template>
    <h2>{{ exam_name }}</h2>
    <h2>{{ exam_token }}</h2>
</template>
