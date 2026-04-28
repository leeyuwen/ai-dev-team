export type AgentStep = 'idle' | 'pm' | 'arch' | 'dev' | 'test' | 'devops' | 'done' | 'error' | 'await_approval'

export interface SSEEvent {
  type: 'status' | 'product_manager' | 'architect' | 'developer' | 'tester' | 'devops' | 'complete' | 'error' | 'await_approval' | 'pm_token'
  data: string | FullResult
  done: boolean
  token?: string   // for pm_token events: incremental token

export interface FullResult {
  requirement: string
  architecture: string
  spec: string
  code: string
  test_report: string
  deployment_plan: string
  history: string[]
}

export interface DevelopmentState {
  requirement: string
  isRunning: boolean
  currentStep: AgentStep
  architecture: string
  spec: string
  code: string
  testReport: string
  deploymentPlan: string
  errorMessage: string
}
