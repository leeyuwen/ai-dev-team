<template>
  <div class="min-h-screen bg-gray-950 text-white">
    <TopBar />

    <main class="max-w-6xl mx-auto px-6 py-8">
      <RequirementInput
        :disabled="store.isRunning"
        :show-reset="hasContent"
        @submit="onSubmit"
        @reset="store.reset()"
      />

      <AgentPipeline
        v-if="store.isRunning || store.currentStep !== 'idle'"
        :current-step="store.currentStep"
        :architecture="store.architecture"
        :spec="store.spec"
        :code="store.code"
        :test-report="store.testReport"
        :deployment-plan="store.deploymentPlan"
        :error-message="store.errorMessage"
        :is-running="store.isRunning"
        class="mt-6"
      />

      <ResultPanel
        v-if="hasContent"
        :architecture="store.architecture"
        :spec="store.spec"
        :code="store.code"
        :test-report="store.testReport"
        :deployment-plan="store.deploymentPlan"
        class="mt-6"
      />

      <ApprovalDialog
        :visible="store.awaitingApproval"
        :spec="store.pendingSpec"
        @approve="onApprove"
        @cancel="onApprovalCancel"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDevelopmentStore } from './stores/development'
import TopBar from './components/TopBar.vue'
import RequirementInput from './components/RequirementInput.vue'
import AgentPipeline from './components/AgentPipeline.vue'
import ResultPanel from './components/ResultPanel.vue'
import ApprovalDialog from './components/ApprovalDialog.vue'

const store = useDevelopmentStore()

const hasContent = computed(() =>
  store.architecture || store.spec || store.code || store.testReport || store.deploymentPlan
)

function onSubmit(requirement: string) {
  store.startDevelopment(requirement)
}

function onApprove(modifiedSpec: string) {
  store.approveSpecFlow(modifiedSpec)
}

function onApprovalCancel() {
  store.reset()
}
</script>
