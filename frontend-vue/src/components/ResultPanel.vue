<template>
  <div class="bg-gray-800 rounded-xl p-6 mt-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-white">📋 开发结果</h2>
    </div>

    <div class="space-y-4">
      <!-- 产品规格 -->
      <details open class="group">
        <summary class="flex items-center gap-2 cursor-pointer list-none text-white font-medium">
          <span class="text-gray-400 group-open:text-blue-400 transition-colors">📋</span>
          <span class="group-open:text-blue-400 transition-colors">产品规格文档</span>
        </summary>
        <div class="mt-3 p-4 bg-gray-900 rounded-lg">
          <pre class="text-sm text-gray-300 whitespace-pre-wrap break-words font-sans">{{ spec }}</pre>
        </div>
      </details>

      <!-- 架构设计 -->
      <details class="group">
        <summary class="flex items-center gap-2 cursor-pointer list-none text-white font-medium">
          <span class="text-gray-400 group-open:text-blue-400 transition-colors">🏗️</span>
          <span class="group-open:text-blue-400 transition-colors">架构设计文档</span>
        </summary>
        <div class="mt-3 p-4 bg-gray-900 rounded-lg">
          <pre class="text-sm text-gray-300 whitespace-pre-wrap break-words font-sans">{{ architecture }}</pre>
        </div>
      </details>

      <!-- 代码实现 -->
      <details class="group">
        <summary class="flex items-center gap-2 cursor-pointer list-none text-white font-medium">
          <span class="text-gray-400 group-open:text-blue-400 transition-colors">💻</span>
          <span class="group-open:text-blue-400 transition-colors">代码实现</span>
        </summary>
        <div class="mt-3 p-4 bg-gray-900 rounded-lg">
          <pre class="text-sm text-gray-300 whitespace-pre-wrap break-words font-sans">{{ code }}</pre>
        </div>
      </details>

      <!-- 测试报告 -->
      <details class="group">
        <summary class="flex items-center gap-2 cursor-pointer list-none text-white font-medium">
          <span class="text-gray-400 group-open:text-blue-400 transition-colors">🧪</span>
          <span class="group-open:text-blue-400 transition-colors">测试报告</span>
        </summary>
        <div class="mt-3 p-4 bg-gray-900 rounded-lg">
          <pre class="text-sm text-gray-300 whitespace-pre-wrap break-words font-sans">{{ testReport }}</pre>
        </div>
      </details>

      <!-- 部署计划 -->
      <details class="group">
        <summary class="flex items-center gap-2 cursor-pointer list-none text-white font-medium">
          <span class="text-gray-400 group-open:text-blue-400 transition-colors">🚢</span>
          <span class="group-open:text-blue-400 transition-colors">部署计划</span>
        </summary>
        <div class="mt-3 p-4 bg-gray-900 rounded-lg">
          <pre class="text-sm text-gray-300 whitespace-pre-wrap break-words font-sans">{{ deploymentPlan }}</pre>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  architecture: string
  spec: string
  code: string
  testReport: string
  deploymentPlan: string
}>()
</script>
