**
 * 简单计算器 - 核心逻辑
 * 使用 BigNumber.js 处理高精度计算
 */

class Calculator {
    constructor() {
        // 状态管理
        this.currentValue = '0';      // 当前显示值
        this.previousValue = null;    // 前一个值
        this.operator = null;         // 当前运算符
        this.waitingForOperand = false; // 等待下一个操作数
        this.expression = '';         // 表达式显示
        
        // DOM 元素引用
        this.displayElement = document.getElementById('result');
        this.expressionElement = document.getElementById('expression');
        
        // 初始化
        this.init();
    }
    
    init() {
        // 绑定按钮事件
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', (e) => this.handleButtonClick(e));
        });
        
        // 键盘支持
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // 初始显示
        this.updateDisplay();
    }
    
    /**
     * 处理按钮点击
     */
    handleButtonClick(event) {
        const button = event.currentTarget;
        const action = button.dataset.action;
        const value = button.dataset.value;
        
        // 添加点击动画
        button.classList.add('pressed');
        setTimeout(() => button.classList.remove('pressed'), 100);
        
        // 清除运算符高亮
        this.clearOperatorHighlight();
        
        // 根据操作类型处理
        if (button.classList.contains('number')) {
            this.inputNumber(value);
        } else if (action === 'operator') {
            this.setOperator(value);
            // 高亮当前运算符
            this.highlightOperator(button);
        } else if (action === 'calculate') {
            this.calculate();
        } else if (action === 'decimal') {
            this.inputDecimal();
        } else if (action === 'clear-all') {
            this.clearAll();
        } else if (action === 'clear') {
            this.clear();
        } else if (action === 'backspace') {
            this.backspace();
        } else if (action === 'toggle-sign') {
            this.toggleSign();
        } else if (action === 'percentage') {
            this.percentage();
        }
    }
    
    /**
     * 处理键盘输入
     */
    handleKeyboard(event) {
        const key = event.key;
        const keyMap = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '.': '.', '+': '+', '-': '-', '*': '×', '/': '÷',
            'Enter': '=', '=': '=', 'Escape': 'AC', 'Backspace': '⌫'
        };
        
        if (keyMap[key]) {
            event.preventDefault();
            
            // 模拟按钮点击效果
            const buttonValue = keyMap[key];
            const button = this.findButton(buttonValue);
            if (button) {
                button.classList.add('pressed');
                setTimeout(() => button.classList.remove('pressed'), 100);
            }
            
            // 根据按键执行对应操作
            if (/^[0-9]$/.test(key)) {
                this.inputNumber(key);
            } else if (key === '.') {
                this.inputDecimal();
            } else if (key === '+' || key === '-') {
                this.setOperator(key === '+' ? '+' : '−');
            } else if (key === '*' || key === '/') {
                this.setOperator(key === '*' ? '×' : '÷');
            } else if (key === 'Enter' || key === '=') {
                this.calculate();
            } else if (key === 'Escape') {
                this.clearAll();
            } else if (key === 'Backspace') {
                this.backspace();
            }
        }
    }
    
    /**
     * 查找对应按钮
     */
    findButton(value) {
        return document.querySelector(`.btn[data-value="${value}"]`) ||
               document.querySelector(`.btn[data-action="calculate"]`);
    }
    
    /**
     * 输入数字
     */
    inputNumber(num) {
        // 如果等待下一个操作数，替换当前值
        if (this.waitingForOperand) {
            this.currentValue = num;
            this.waitingForOperand = false;
        } else {
            // 限制数字长度
            if (this.currentValue.replace('-', '').replace('.', '').length >= 12) {
                return;
            }
            
            // 处理0开头的特殊情况
            if (this.currentValue === '0' && num !== '0') {
                this.currentValue = num;
            } else if (this.currentValue === '0' && num === '0') {
                // 多个0不处理
            } else if (this.currentValue === '-0') {
                this.currentValue = '-' + num;
            } else {
                this.currentValue += num;
            }
        }
        
        this.updateDisplay();
    }
    
    /**
     * 输入小数点
     */
    inputDecimal() {
        if (this.waitingForOperand) {
            this.currentValue = '0.';
            this.waitingForOperand = false;
        } else if (!this.currentValue.includes('.')) {
            this.currentValue += '.';
        }
        
        this.updateDisplay();
    }
    
    /**
     * 设置运算符
     */
    setOperator(nextOperator) {
        const inputValue = this.getCurrentValue();
        
        // 如果已有运算符和前值，先计算
        if (this.operator && !this.waitingForOperand) {
            const result = this.performCalculation();
            if (result === 'Error') {
                this.displayError();
                return;
            }
            this.currentValue = result;
            this.previousValue = result;
        } else {
            this.previousValue = inputValue;
        }
        
        this.operator = nextOperator;
        this.waitingForOperand = true;
        
        // 更新表达式显示
        this.updateExpression();
    }
    
    /**
     * 执行计算
     */
    calculate() {
        if (!this.operator || this.waitingForOperand) {
            return;
        }
        
        const result = this.performCalculation();
        
        if (result === 'Error') {
            this.displayError();
            return;
        }
        
        // 保存结果用于连续运算
        this.previousValue = this.currentValue;
        this.currentValue = result;
        this.operator = null;
        this.waitingForOperand = true;
        
        // 更新表达式显示（显示完整表达式）
        this.updateExpression(true);
        
        this.updateDisplay();
    }
    
    /**
     * 执行具体计算逻辑
     */
    performCalculation() {
        const prev = new BigNumber(this.previousValue || '0');
        const current = new BigNumber(this.currentValue);
        let result;
        
        try {
            switch (this.operator) {
                case '+':
                    result = prev.plus(current);
                    break;
                case '−':
                case '-':
                    result = prev.minus(current);
                    break;
                case '×':
                case '*':
                    result = prev.times(current);
                    break;
                case '÷':
                case '/':
                    if (current.isZero()) {
                        return 'Error'; // 除数为零
                    }
                    result = prev.dividedBy(current);
                    break;
                default:
                    return this.currentValue;
            }
            
            // 格式化结果
            let formattedResult = result.toString();
            
            // 如果结果太长，保留合理精度
            if (formattedResult.length > 12) {
                formattedResult = result.toPrecision(10);
            }
            
            // 移除尾部无效的0
            formattedResult = new BigNumber(formattedResult).toString();
            
            return formattedResult;
            
        } catch (error) {
            console.error('Calculation error:', error);
            return 'Error';
        }
    }
    
    /**
     * 获取当前值（BigNumber）
     */
    getCurrentValue() {
        return this.currentValue;
    }
    
    /**
     * 清除全部
     */
    clearAll() {
        this.currentValue = '0';
        this.previousValue = null;
        this.operator = null;
        this.waitingForOperand = false;
        this.expression = '';
        this.updateDisplay();
        this.expressionElement.textContent = '';
    }
    
    /**
     * 清除当前输入
     */
    clear() {
        this.currentValue = '0';
        this.updateDisplay();
    }
    
    /**
     * 退格
     */
    backspace() {
        if (this.waitingForOperand) {
            return;
        }
        
        if (this.currentValue.length > 1) {
            this.currentValue = this.currentValue.slice(0, -1);
        } else {
            this.currentValue = '0';
        }
        
        this.updateDisplay();
    }
    
    /**
     * 切换正负号
     */
    toggleSign() {
        if (this.currentValue === '0') {
            return;
        }
        
        if (this.currentValue.startsWith('-')) {
            this.currentValue = this.currentValue.slice(1);
        } else {
            this.currentValue = '-' + this.currentValue;
        }
        
        this.updateDisplay();
    }
    
    /**
     * 百分比
     */
    percentage() {
        const value = new BigNumber(this.currentValue);
        this.currentValue = value.dividedBy(100).toString();
        this.updateDisplay();
    }
    
    /**
     * 更新显示
     */
    updateDisplay() {
        // 格式化显示值
        let displayValue = this.currentValue;
        
        // 特殊处理
        if (displayValue === 'Error') {
            this.displayElement.textContent = 'Error';
            this.displayElement.classList.add('error');
            return;
        }
        
        this.displayElement.classList.remove('error');
        
        // 移除尾部多余的点和0
        if (displayValue.includes('.')) {
            displayValue = displayValue.replace(/\.?0+$/, '');
        }
        
        // 调整字号以适应长度
        this.displayElement.classList.remove('long-number', 'very-long-number');
        if (displayValue.length > 9) {
            this.displayElement.classList.add('very-long-number');
        } else if (displayValue.length > 7) {
            this.displayElement.classList.add('long-number');
        }
        
        this.displayElement.textContent = displayValue;
    }
    
    /**
     * 更新表达式显示
     */
    updateExpression(showResult = false) {
        if (showResult) {
            // 显示完整计算表达式
            const prev = this.previousValue;
            const curr = this.currentValue;
            this.expressionElement.textContent = `${prev} ${this.operator} ${curr} =`;
        } else {
            // 显示当前输入的表达式
            if (this.previousValue && this.operator) {
                this.expressionElement.textContent = `${this.previousValue} ${this.operator}`;
            }
        }
    }
    
    /**
     * 显示错误
     */
    displayError() {
        this.currentValue = 'Error';
        this.previousValue = null;
        this.operator = null;
        this.waitingForOperand = false;
        this.expression = '';
        this.expressionElement.textContent = '';
        this.updateDisplay();
    }
    
    /**
     * 高亮运算符按钮
     */
    highlightOperator(button) {
        document.querySelectorAll('.btn.operator').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
    }
    
    /**
     * 清除运算符高亮
     */
    clearOperatorHighlight() {
        document.querySelectorAll('.btn.operator').forEach(btn => {
            btn.classList.remove('active');
        });
    }
}

// 页面加载完成后初始化计算器
document.addEventListener('DOMContentLoaded', () => {
    window.calculator = new Calculator();
});