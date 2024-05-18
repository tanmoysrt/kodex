<script setup>
import { Toasts } from 'frappe-ui'
</script>
<template>
  <div class="p-4 select-none">
    <Toasts />
    <router-view />
  </div>
</template>
<style>
.custom-scroll::-webkit-scrollbar {
  width: 9px;
  height: 9px;
}

.custom-scroll::-webkit-scrollbar-track {
  @apply rounded-full bg-gray-200;
}

.custom-scroll::-webkit-scrollbar-thumb {
  @apply rounded-full bg-black;
}




</style>

<!--body {-->
<!--background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='200px' width='200px'><text transform='translate(20, 100) rotate(-45)' fill='rgb(210,210,210)' font-size='20'>watermark</text></svg>");-->
<!--}-->