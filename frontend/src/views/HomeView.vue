<script setup>
import { useRouter } from 'vue-router';
import logoImg from '@/assets/logo.png';

const router = useRouter();

const goLogin = () => router.push('/login');
</script>

<template>
  <div class="page">
    <!-- Navbar -->
    <header class="navbar">
      <div class="navbar-brand">
        <img :src="logoImg" class="nav-logo" alt="Pathfinder logo" />
        <span class="nav-title">Pathfinder.Ai</span>
      </div>
      <div class="navbar-right">
        <button class="brutal-btn" @click="goLogin">LOGIN / SIGNUP</button>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="main">
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">NAVIGATE YOUR <span class="highlight">CAREER PATH</span> WITH AI.</h1>
          <p class="hero-subtitle">
            Pathfinder.Ai is the ultimate career co-pilot. Build tailored resumes, get actionable LeetCode insights, and explore thousands of aggregated job postings in one unified dashboard.
          </p>
          <div class="hero-actions">
            <button class="primary-btn" @click="goLogin">
              GET STARTED NOW
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        </div>
        <div class="hero-graphic">
          <!-- Abstract Neo-Brutalist shapes -->
          <div class="shape box shape-1"></div>
          <div class="shape box shape-2"></div>
          <div class="shape box shape-3">
            <h3 class="shape-text">JOB<br/>READY</h3>
          </div>
        </div>
      </section>

      <!-- Features Grid -->
      <section class="features-section">
        <h2 class="section-heading">CORE CAPABILITIES</h2>
        <div class="features-grid">

          <div class="feature-card box bg-blue">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <h3 class="feature-title">AI Resume Tailoring</h3>
            <p class="feature-desc">Generate ATS-friendly resumes perfectly tailored to your target roles using advanced LLMs.</p>
          </div>

          <div class="feature-card box bg-purple">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <h3 class="feature-title">LeetCode Analytics</h3>
            <p class="feature-desc">Connect your LeetCode profile to receive personalized study advice and interview readiness metrics.</p>
          </div>

          <div class="feature-card box bg-green">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            </div>
            <h3 class="feature-title">Job Aggregation</h3>
            <p class="feature-desc">Explore thousands of active job postings harvested daily from top remote boards and LinkedIn.</p>
          </div>

          <div class="feature-card box bg-yellow">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <h3 class="feature-title">Direct Company Hiring</h3>
            <p class="feature-desc">Companies can register, get verified, and post roles directly to our student network.</p>
          </div>

        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="footer-content">
        <span class="footer-text">© 2026 Pathfinder.Ai • Engineered for scale</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page {
  display: flex;  flex-direction: column;}
/* ── Navbar ─────────────────────────────────────────────── */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  height: 68px;
  background: #fff;
  border-bottom: 2px solid #111;
  box-shadow: 0 4px 0 #111;
}
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.nav-logo {
  height: 48px;
  width: 48px;
  object-fit: contain;
}
.nav-title {
  font-weight: 900;
  font-size: 20px;
  letter-spacing: -0.5px;
  text-transform: uppercase;
}
/* ── Main Layout ────────────────────────────────────────── */
.main {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 28px;
  display: flex;
  flex-direction: column;
  gap: 80px;
}
/* ── Hero Section ───────────────────────────────────────── */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}
.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero-title {
  font-size: 54px;
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -1.5px;
  text-transform: uppercase;
}
.highlight {
  background: #ffeaa7;
  padding: 0 8px;
  border: 2px solid var(--ink);
  box-shadow: 4px 4px 0 var(--ink);
  display: inline-block;
  transform: rotate(-1deg);
}
.hero-subtitle {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.5;
  opacity: 0.85;
  max-width: 90%;
}
.primary-btn { display: inline-flex; align-items: center; gap: 12px; }
.hero-graphic {
  position: relative;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.shape {
  position: absolute;
}
.shape-1 {
  width: 250px;
  height: 250px;
  background: #74b9ff;
  border-radius: 50%;
  top: 20px;
  left: 40px;
}
.shape-2 {
  width: 200px;
  height: 200px;
  background: #55efc4;
  bottom: 40px;
  right: 60px;
  transform: rotate(15deg);
}
.shape-3 {
  width: 180px;
  height: 120px;
  background: #ff7675;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(-10deg);
}
.shape-text {
  font-size: 28px;
  font-weight: 900;
  text-align: center;
  color: var(--ink);
  line-height: 1;
}
/* ── Features Section ───────────────────────────────────── */
.features-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.section-heading {
  font-size: 24px;
  font-weight: 900;
  text-transform: uppercase;
  text-decoration: underline;
  text-underline-offset: 6px;
  text-decoration-thickness: 3px;
  text-align: center;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}
.feature-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: transform 0.2s;
}
.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 6px 8px 0 var(--ink);
}
.bg-blue { background: #74b9ff; }
.bg-purple { background: #a29bfe; }
.bg-green { background: #55efc4; }
.bg-yellow { background: #ffeaa7; }
.feature-icon {
  width: 48px;
  height: 48px;
  background: var(--surface);
  border: 2px solid var(--ink);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.feature-title {
  font-size: 18px;
  font-weight: 900;
  line-height: 1.2;
}
.feature-desc {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1.4;
}
/* ── Footer ─────────────────────────────────────────────── */
.footer {
  border-top: 2px solid var(--ink);
  background: var(--surface);
  padding: 24px;
  text-align: center;
}
.footer-text {
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 1024px) {
  .hero-section { grid-template-columns: 1fr; text-align: center; }
.hero-content { align-items: center; }
.hero-graphic { display: none; }
.features-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .hero-title { font-size: 40px; }
.features-grid { grid-template-columns: 1fr; }
.navbar { padding: 0 16px; }
}
</style>
