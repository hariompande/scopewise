<template>
  <div class="space-y-2">
    <div v-for="i in 3" :key="i" class="p-3 bg-red-50 rounded-md animate-pulse">
      <div class="h-4 bg-red-200 rounded w-3/4 mb-2"></div>
      <div class="h-3 bg-red-200 rounded w-1/2"></div>
    </div>
  </div>
</template>
