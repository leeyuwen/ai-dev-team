<template>
  <div class="bg-gray-800 rounded-xl p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-semibold text-white">执行流水线</h2>
      <span class="text-sm text-gray-400">{{ progress }}%</span>
    </div>

    <!-- Progress bar -->
    <div class="w-full bg-gray-700 rounded-full h-2 mb-8">
      <div
        class="bg-blue-500 h-2 rounded-full transition-all duration-500"
        :style="{ width: `${progress}%` }"
      />
    </div>

    <!-- Agent steps -->
    <div class="grid grid-cols-5 gap-4">
      <AgentCard
        v-for="agent in agents"
        :key="agent.key"
        :agent-key="agent.key"
        :label="agent.label"
        :icon="agent.icon"
        :content="getContent(agent.key)"
        :is-active="currentStep === agent.key"
        :is-done="isDone(agent.key)"
      />
    </div>

    <!-- Error display -->
    <div v-if="errorMessage" class="mt-6 p-4 bg-red-900/50 border border-red-700 rounded-lg">
      <p class="text-red-300 text-sm">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentStep } from '../types'
import AgentCard from './AgentCard.vue'

const props = defineProps<{
  currentStep: AgentStep
  architecture: string
  spec: string
  code: string
  testReport: string
  deploymentPlan: string
  errorMessage: string
  isRunning: boolean
}>()

const progress = computed(() => {
  const map: Record<AgentStep, number> = {
    idle: 0, pm: 25, dev: 50, test: 75, devops: 90, done: 100, error: 0
  }
  return map[props.currentStep]
})

const agents = [
  { key: 'pm' as AgentStep, label: '产品经理', icon: '📋' },
  { key: 'arch' as AgentStep, label: '架构师', icon: '🏗️' },
  { key: 'dev' as AgentStep, label: '开发工程师', icon: '💻' },
  { key: 'test' as AgentStep, label: '测试工程师', icon: '🧪' },
  { key: 'devops' as AgentStep, label: '部署工程师', icon: '🚢' },
]

function getContent(key: AgentStep): string {
  const map: Record<AgentStep, string> = {
    idle: '', pm: props.spec, arch: props.architecture, dev: props.code,
    test: props.testReport, devops: props.deploymentPlan, done: '', error: ''
  }
  return map[key]
}

function isDone(key: AgentStep): boolean {
  const order: AgentStep[] = ['pm', 'arch', 'dev', 'test', 'devops', 'done']
  const currentIdx = order.indexOf(props.currentStep)
  return order.indexOf(key) < currentIdx || props.currentStep === 'done'
}
</script>
