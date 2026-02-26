<script setup>
// Jobs page — coming soon
</script>

<template>
  <div class="page">
    <NavBar />
    <div class="coming-soon">
      <div class="box">
        <p class="label">COMING SOON</p>
        <h1 class="title">Jobs</h1>
        <p class="sub">AI-matched career opportunities will appear here.</p>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default { components: { NavBar } };
</script>

<style scoped>
.page { min-height: 100vh; background: #DEDEDE; }
.coming-soon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 68px);
}
.box {
  background: #fff;
  border: 2px solid #111;
  box-shadow: 5px 5px 0 #111;
  padding: 48px 60px;
  text-align: center;
}
.label {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.5;
  margin-bottom: 10px;
}
.title {
  font-size: 48px;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.sub {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.6;
  font-style: italic;
}
</style>
