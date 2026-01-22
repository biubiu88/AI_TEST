<template>
  <div class="reset-container">
    <div class="reset-box">
      <div class="reset-header">
        <el-icon :size="48" color="#409eff">
          <Key />
        </el-icon>
        <h1>重置密码</h1>
        <p>通过邮箱重置您的账户密码</p>
      </div>
      
      <el-form 
        ref="resetFormRef"
        :model="resetForm" 
        :rules="resetRules"
        class="reset-form"
      >
        <el-form-item prop="email">
          <el-input 
            v-model="resetForm.email" 
            prefix-icon="Message"
            placeholder="请输入注册邮箱"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="newPassword">
          <el-input 
            v-model="resetForm.newPassword" 
            prefix-icon="Lock"
            type="password"
            placeholder="请输入新密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="resetForm.confirmPassword" 
            prefix-icon="Lock"
            type="password"
            placeholder="请确认新密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading"
            @click="handleReset" 
            style="width: 100%"
          >
            重置密码
          </el-button>
        </el-form-item>
        <el-form-item>
          <div class="back-link">
            <el-link type="primary" @click="goToLogin">
              <el-icon><ArrowLeft /></el-icon>
              返回登录
            </el-link>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Key, ArrowLeft } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const resetFormRef = ref(null)
const loading = ref(false)

const resetForm = reactive({
  email: '',
  newPassword: '',
  confirmPassword: ''
})

// 验证确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== resetForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const resetRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleReset = async () => {
  if (!resetFormRef.value) return
  
  await resetFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await userStore.resetPassword(resetForm)
      ElMessage.success('密码重置成功，请使用新密码登录')
      router.push('/login')
    } catch (error) {
      // 错误已在拦截器中处理
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.reset-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.reset-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.reset-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    margin: 15px 0 10px;
    font-size: 24px;
    color: #303133;
  }
  
  p {
    color: #909399;
    font-size: 14px;
  }
}

.reset-form {
  :deep(.el-input__wrapper) {
    padding: 8px 15px;
  }
}

.back-link {
  width: 100%;
  text-align: center;
  
  .el-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
}
</style>
