<script setup>
import { Toasts } from 'frappe-ui'
</script>
<template>
  <div id="test" class="p-4 select-none">
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
