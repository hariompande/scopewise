<template>
  <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
    <div v-for="i in 6" :key="i" class="p-3 bg-gray-50 rounded-md animate-pulse">
      <div class="h-3 bg-gray-200 rounded w-16 mb-2"></div>
      <div class="h-4 bg-gray-300 rounded w-20"></div>
    </div>
  </div>
</template>
