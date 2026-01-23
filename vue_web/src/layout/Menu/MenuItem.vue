<template>
  <template v-for="item in menuList" :key="item.path || item.name">
    <!-- 有子菜单 -->
    <el-sub-menu v-if="item.children && item.children.length > 0 && !item.meta?.hidden" :index="item.path || item.name">
      <template #title>
        <el-icon v-if="item.meta?.icon">
          <component :is="item.meta.icon" />
        </el-icon>
        <span>{{ item.meta?.title || item.name }}</span>
      </template>
      <menu-item :menu-list="item.children" />
    </el-sub-menu>
    <!-- 无子菜单 -->
    <el-menu-item v-else-if="!item.meta?.hidden" :index="item.path">
      <el-icon v-if="item.meta?.icon">
        <component :is="item.meta.icon" />
      </el-icon>
      <template #title>{{ item.meta?.title || item.name }}</template>
    </el-menu-item>
  </template>
</template>

<script setup>
defineProps({
  menuList: {
    type: Array,
    default: () => []
  }
})
</script>
