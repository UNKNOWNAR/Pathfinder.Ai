<script setup>
// LeetCode page — coming soon
</script>

<template>
  <div class="page">
    <NavBar />
    <div class="coming-soon">
      <div class="box">
        <p class="label">COMING SOON</p>
        <h1 class="title">LeetCode</h1>
        <p class="sub">AI-curated practice problems tailored to your target roles will appear here.</p>
        <div class="tags">
          <span class="tag">Arrays</span>
          <span class="tag">Dynamic Programming</span>
          <span class="tag">Graphs</span>
          <span class="tag">System Design</span>
        </div>
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.label {
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.5;
}
.title {
  font-size: 48px;
  font-weight: 900;
  text-transform: uppercase;
}
.sub {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.6;
  font-style: italic;
  max-width: 340px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 8px;
}
.tag {
  background: #2d8cf0;
  color: #fff;
  border: 2px solid #111;
  box-shadow: 2px 2px 0 #111;
  padding: 5px 12px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
