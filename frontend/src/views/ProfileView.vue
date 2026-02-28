<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import api from '@/services/api';

const defaultProfile = () => ({
  name:       '',
  headline:   '',
  github:     '',
  linkedin:   '',
  portfolio:  '',
  leetcode_username: '',
  email:      '',
  phone:      '',
  location:   '',
  summary:    '',
  skills:     [],
  experience: [],
  education:  [],
  projects:   [],
  achievements: [],
  photo:      null,
});

const profile = reactive(defaultProfile());

const isSaving = ref(false);
const isGenerating = ref(false);

onMounted(async () => {
  try {
    const res = await api.get('/profile');
    if (res.data) {
      Object.assign(profile, res.data);
      // Ensure arrays are initialized if null in DB
      profile.skills = res.data.skills || [];
      profile.experience = res.data.experience || [];
      profile.education = res.data.education || [];
      profile.projects = res.data.projects || [];
      profile.achievements = res.data.achievements || [];
    }
  } catch (err) {
    if (err.response?.status !== 404) {
      console.error("Error fetching profile", err);
    }
  }
});

const skillInput = ref('');
const openSections = reactive({
  personal:     true,
  skills:       false,
  experience:   false,
  education:    false,
  projects:     false,
  achievements: false,
  resume:       false,
});

const jdText = ref('');
const saved_msg = ref('');

// ── Photo upload ──────────────────────────────────────────────────────────
const fileInput = ref(null);
const photoPreview = computed(() => profile.photo || null);

const pickPhoto = () => fileInput.value.click();
const onPhotoChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => { profile.photo = ev.target.result; };
  reader.readAsDataURL(file);
};

// ── Skills ────────────────────────────────────────────────────────────────
const addSkill = () => {
  const s = skillInput.value.trim();
  if (s && !profile.skills.includes(s)) profile.skills.push(s);
  skillInput.value = '';
};
const removeSkill = (i) => profile.skills.splice(i, 1);
const onSkillKey = (e) => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); addSkill(); } };

// ── Repeater helpers ──────────────────────────────────────────────────────
const addExp = () => profile.experience.push({ company: '', role: '', duration: '', description: '' });
const removeExp = (i) => profile.experience.splice(i, 1);

const addEdu = () => profile.education.push({ institution: '', degree: '', year: '' });
const removeEdu = (i) => profile.education.splice(i, 1);

const addProject = () => profile.projects.push({ title: '', tech: '', url: '', description: '' });
const removeProject = (i) => profile.projects.splice(i, 1);

const addAchievement = () => profile.achievements.push({ title: '', issuer: '', year: '', description: '' });
const removeAchievement = (i) => profile.achievements.splice(i, 1);

const saveProfile = async () => {
  isSaving.value = true;
  saved_msg.value = 'Saving...';
  try {
    await api.put('/profile', profile);
    saved_msg.value = '✦ SAVED!';
    // Optional: Keep localStorage username in sync if used elsewhere
    localStorage.setItem('username', profile.name);
  } catch (err) {
    console.error(err);
    saved_msg.value = 'FAILED!';
    alert('Failed to save profile. ' + (err.response?.data?.message || ''));
  } finally {
    setTimeout(() => {
      saved_msg.value = '';
      isSaving.value = false;
    }, 2000);
  }
};

const generateResume = async () => {
  if (!jdText.value.trim() || isGenerating.value) return;
  isGenerating.value = true;
  try {
    const res = await api.post('/generate-resume', { jd_text: jdText.value }, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'Pathfinder_Tailored_Resume.pdf');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    console.error(err);
    alert('Failed to generate resume. Please ensure required profile fields are filled.');
  } finally {
    isGenerating.value = false;
  }
};

// ── Toggle accordion ──────────────────────────────────────────────────────
const toggle = (key) => { openSections[key] = !openSections[key]; };
</script>

<template>
  <div class="page">
    <NavBar />

    <div class="content">

      <!-- ── Profile Hero ───────────────────────────────────────────────── -->
      <section class="hero box">

        <!-- Photo -->
        <div class="photo-wrap" @click="pickPhoto" title="Click to change photo">
          <img v-if="photoPreview" :src="photoPreview" class="photo-img" alt="Profile photo" />
          <div v-else class="photo-placeholder">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <span>PHOTO</span>
          </div>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onPhotoChange" />
        </div>

        <!-- Name + headline + links -->
        <div class="hero-info">
          <input
            class="name-input"
            v-model="profile.name"
            placeholder="YOUR NAME"
            maxlength="60"
          />
          <input
            class="headline-input"
            v-model="profile.headline"
            placeholder="Headline — e.g. Full Stack Developer | ML Enthusiast"
          />
          <div class="link-row">
            <div class="link-field">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
              <input v-model="profile.github" placeholder="github.com/username" class="link-input" />
            </div>
            <div class="link-field">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              <input v-model="profile.linkedin" placeholder="linkedin.com/in/username" class="link-input" />
            </div>
            <div class="link-field">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              <input v-model="profile.portfolio" placeholder="yourportfolio.com" class="link-input" />
            </div>
            <div class="link-field" title="LeetCode Username">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M16.102 17.93l-2.697 2.607c-.466.467-1.111.662-1.823.662s-1.357-.195-1.824-.662l-4.332-4.363c-.467-.467-.702-1.15-.702-1.863s.235-1.357.702-1.824l4.319-4.38c.467-.467 1.125-.645 1.837-.645s1.357.195 1.823.662l2.697 2.606c.514.515 1.365.497 1.9-.038.535-.536.553-1.387.039-1.901l-2.609-2.636a5.055 5.055 0 0 0-2.445-1.337l2.467-2.503c.516-.514.498-1.366-.037-1.901-.535-.535-1.387-.552-1.902-.038l-10.1 10.101c-.981.982-1.469 2.406-1.469 3.896 0 1.486.487 2.915 1.469 3.897l5.622 5.623c.982.982 2.364 1.536 3.846 1.536 1.486 0 2.868-.554 3.846-1.536l2.898-2.896c.515-.515.533-1.367-.038-1.901-.536-.535-1.387-.553-1.902-.038z"/></svg>
              <input v-model="profile.leetcode_username" placeholder="leetcode_username" class="link-input" />
            </div>
          </div>
        </div>

        <!-- Save -->
        <div class="hero-actions">
          <button class="save-btn" @click="saveProfile" :disabled="isSaving">
            {{ saved_msg || '✦ SAVE PROFILE' }}
          </button>
        </div>
      </section>

      <!-- ── Accordion sections ─────────────────────────────────────────── -->

      <!-- Personal Info -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('personal')">
          <span>PERSONAL INFO</span>
          <span class="chevron" :class="{ open: openSections.personal }">▼</span>
        </button>
        <div v-if="openSections.personal" class="accord-body">
          <div class="field-grid">
            <div class="field">
              <label>Email</label>
              <input v-model="profile.email" placeholder="you@email.com" />
            </div>
            <div class="field">
              <label>Phone</label>
              <input v-model="profile.phone" placeholder="+91 9876543210" />
            </div>
            <div class="field">
              <label>Location</label>
              <input v-model="profile.location" placeholder="City, Country" />
            </div>
          </div>
          <div class="field full">
            <label>Summary / About</label>
            <textarea v-model="profile.summary" rows="3" placeholder="Brief intro about yourself..."></textarea>
          </div>
        </div>
      </div>

      <!-- Skills -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('skills')">
          <span>SKILLS</span>
          <span class="chevron" :class="{ open: openSections.skills }">▼</span>
        </button>
        <div v-if="openSections.skills" class="accord-body">
          <div class="skill-input-row">
            <input
              v-model="skillInput"
              placeholder="Type a skill and press Enter"
              @keydown="onSkillKey"
              class="skill-input"
            />
            <button class="add-btn" @click="addSkill">+ Add</button>
          </div>
          <div class="chips">
            <span v-for="(sk, i) in profile.skills" :key="i" class="chip">
              {{ sk }}
              <button class="chip-remove" @click="removeSkill(i)">×</button>
            </span>
            <span v-if="!profile.skills.length" class="empty-hint">No skills added yet.</span>
          </div>
        </div>
      </div>

      <!-- Experience -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('experience')">
          <span>EXPERIENCE</span>
          <span class="chevron" :class="{ open: openSections.experience }">▼</span>
        </button>
        <div v-if="openSections.experience" class="accord-body">
          <div v-for="(exp, i) in profile.experience" :key="i" class="repeater-card">
            <div class="repeater-header">
              <strong>Experience {{ i + 1 }}</strong>
              <button class="remove-btn" @click="removeExp(i)">✕ Remove</button>
            </div>
            <div class="field-grid">
              <div class="field">
                <label>Company</label>
                <input v-model="exp.company" placeholder="Company name" />
              </div>
              <div class="field">
                <label>Role</label>
                <input v-model="exp.role" placeholder="Software Engineer" />
              </div>
              <div class="field">
                <label>Duration</label>
                <input v-model="exp.duration" placeholder="Jan 2024 – Present" />
              </div>
            </div>
            <div class="field full">
              <label>Description</label>
              <textarea v-model="exp.description" rows="2" placeholder="Key responsibilities and achievements..."></textarea>
            </div>
          </div>
          <button class="add-entry-btn" @click="addExp">+ Add Experience</button>
        </div>
      </div>

      <!-- Education -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('education')">
          <span>EDUCATION</span>
          <span class="chevron" :class="{ open: openSections.education }">▼</span>
        </button>
        <div v-if="openSections.education" class="accord-body">
          <div v-for="(edu, i) in profile.education" :key="i" class="repeater-card">
            <div class="repeater-header">
              <strong>Education {{ i + 1 }}</strong>
              <button class="remove-btn" @click="removeEdu(i)">✕ Remove</button>
            </div>
            <div class="field-grid">
              <div class="field">
                <label>Institution</label>
                <input v-model="edu.institution" placeholder="University / College" />
              </div>
              <div class="field">
                <label>Degree</label>
                <input v-model="edu.degree" placeholder="B.Tech Computer Science" />
              </div>
              <div class="field">
                <label>Year</label>
                <input v-model="edu.year" placeholder="2021 – 2025" />
              </div>
            </div>
          </div>
          <button class="add-entry-btn" @click="addEdu">+ Add Education</button>
        </div>
      </div>

      <!-- Projects -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('projects')">
          <span>PROJECTS</span>
          <span class="chevron" :class="{ open: openSections.projects }">▼</span>
        </button>
        <div v-if="openSections.projects" class="accord-body">
          <div v-for="(proj, i) in profile.projects" :key="i" class="repeater-card">
            <div class="repeater-header">
              <strong>Project {{ i + 1 }}</strong>
              <button class="remove-btn" @click="removeProject(i)">✕ Remove</button>
            </div>
            <div class="field-grid">
              <div class="field">
                <label>Title</label>
                <input v-model="proj.title" placeholder="Project name" />
              </div>
              <div class="field">
                <label>Tech Stack</label>
                <input v-model="proj.tech" placeholder="Vue, Python, PostgreSQL" />
              </div>
              <div class="field">
                <label>URL</label>
                <input v-model="proj.url" placeholder="github.com/..." />
              </div>
            </div>
            <div class="field full">
              <label>Description</label>
              <textarea v-model="proj.description" rows="2" placeholder="What it does and your role..."></textarea>
            </div>
          </div>
          <button class="add-entry-btn" @click="addProject">+ Add Project</button>
        </div>
      </div>

      <!-- Achievements -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('achievements')">
          <span>ACHIEVEMENTS</span>
          <span class="chevron" :class="{ open: openSections.achievements }">▼</span>
        </button>
        <div v-if="openSections.achievements" class="accord-body">
          <div v-for="(ach, i) in profile.achievements" :key="i" class="repeater-card">
            <div class="repeater-header">
              <strong>Achievement {{ i + 1 }}</strong>
              <button class="remove-btn" @click="removeAchievement(i)">✕ Remove</button>
            </div>
            <div class="field-grid">
              <div class="field">
                <label>Title</label>
                <input v-model="ach.title" placeholder="e.g. Best Paper Award, Dean's List, Hackathon Winner" />
              </div>
              <div class="field">
                <label>Issuer</label>
                <input v-model="ach.issuer" placeholder="e.g. IEEE, Google, AICTE, University" />
              </div>
              <div class="field">
                <label>Year</label>
                <input v-model="ach.year" placeholder="2024" />
              </div>
            </div>
            <div class="field full">
              <label>Description</label>
              <textarea v-model="ach.description" rows="2" placeholder="Brief description of the achievement..."></textarea>
            </div>
          </div>
          <button class="add-entry-btn" @click="addAchievement">+ Add Achievement</button>
        </div>
      </div>

      <!-- Generate Resume -->
      <div class="accord box">
        <button class="accord-head" @click="toggle('resume')">
          <span>✦ GENERATE RESUME</span>
          <span class="chevron" :class="{ open: openSections.resume }">▼</span>
        </button>
        <div v-if="openSections.resume" class="accord-body">
          <div class="field full">
            <label>Job Description / Role you're targeting</label>
            <textarea
              v-model="jdText"
              rows="5"
              placeholder="Paste the job description here. The AI will tailor your resume to this role..."
            ></textarea>
          </div>
          <button class="generate-btn" @click="generateResume" :disabled="!jdText.trim() || isGenerating">
            {{ isGenerating ? 'GENERATING...' : '✦ GENERATE TAILORED RESUME →' }}
          </button>
          <p class="generate-note">The AI will rewrite your bullets to match the JD, then compile a beautifully formatted PDF.</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ── Tokens ─────────────────────────────────────────────────────────── */
.page {
  --ink:     #111111;
  --bg:      #DEDEDE;
  --surface: #FFFFFF;
  --accent:  #2d8cf0;
  --border:  2px solid var(--ink);
  --shadow:  4px 4px 0 var(--ink);

  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Segoe UI', sans-serif;
}

/* ── Content ─────────────────────────────────────────────────────────── */
.content {
  width: 100%;
  padding: 24px 32px 60px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Shared box / button ─────────────────────────────────────────────── */
.box {
  background: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
}

.outline-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  padding: 8px 16px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  color: var(--ink);
  transition: box-shadow 0.1s, transform 0.1s;
}
.outline-btn:hover  { background: #f0f0f0; }
.outline-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }

/* ── Hero ────────────────────────────────────────────────────────────── */
.hero {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  padding: 24px;
  flex-wrap: wrap;
}

.photo-wrap {
  width: 110px;
  height: 110px;
  flex-shrink: 0;
  background: var(--accent);
  border: var(--border);
  box-shadow: var(--shadow);
  cursor: pointer;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: opacity 0.15s;
}
.photo-wrap:hover { opacity: 0.85; }
.photo-img { width: 100%; height: 100%; object-fit: cover; }

.hero-info {
  flex: 1;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.name-input {
  font-size: 26px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.5px;
  border: none;
  border-bottom: 2px solid var(--ink);
  background: transparent;
  outline: none;
  width: 100%;
  padding: 2px 0;
}
.name-input::placeholder { color: #aaa; }

.headline-input {
  font-size: 14px;
  font-weight: 600;
  font-style: italic;
  border: none;
  border-bottom: 1px dashed #999;
  background: transparent;
  outline: none;
  width: 100%;
  padding: 2px 0;
  color: #555;
}
.headline-input::placeholder { color: #bbb; }

.link-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}

.link-field {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid #ccc;
  padding: 5px 10px;
  background: #fafafa;
}

.link-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 12px;
  font-weight: 600;
  width: 100%;
  color: var(--ink);
}
.link-input::placeholder { color: #bbb; }

.hero-actions {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 10px;
}

.save-btn {
  background: var(--accent);
  border: var(--border);
  box-shadow: var(--shadow);
  padding: 12px 20px;
  font-weight: 900;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  color: var(--ink);
  transition: box-shadow 0.1s, transform 0.1s;
  white-space: nowrap;
}
.save-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(3px,3px); }

/* ── Accordion ───────────────────────────────────────────────────────── */
.accord-head {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: transparent;
  border: none;
  font-weight: 900;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  cursor: pointer;
  color: var(--ink);
  text-align: left;
}
.accord-head:hover { background: #fafafa; }

.chevron {
  font-size: 11px;
  transition: transform 0.2s;
  display: inline-block;
}
.chevron.open { transform: rotate(180deg); }

.accord-body {
  border-top: var(--border);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Form fields ─────────────────────────────────────────────────────── */
.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.field.full { grid-column: 1 / -1; }

.field label {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  opacity: 0.6;
}

.field input,
.field textarea,
.accord-body input,
.accord-body textarea {
  border: var(--border);
  background: var(--surface);
  padding: 9px 12px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  outline: none;
  width: 100%;
  resize: vertical;
  transition: background 0.15s;
  box-shadow: 2px 2px 0 var(--ink);
}
.field input:focus,
.field textarea:focus,
.accord-body input:focus,
.accord-body textarea:focus { background: #fffdf0; }

/* ── Skills chips ────────────────────────────────────────────────────── */
.skill-input-row {
  display: flex;
  gap: 10px;
}
.skill-input {
  flex: 1;
  border: var(--border) !important;
  padding: 9px 12px !important;
  box-shadow: 2px 2px 0 var(--ink) !important;
}
.add-btn {
  border: var(--border);
  box-shadow: 3px 3px 0 var(--ink);
  background: var(--surface);
  padding: 8px 16px;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: box-shadow 0.1s, transform 0.1s;
}
.add-btn:active { box-shadow: 1px 1px 0 var(--ink); transform: translate(2px,2px); }

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--accent);
  border: var(--border);
  box-shadow: 2px 2px 0 var(--ink);
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}
.chip-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 900;
  line-height: 1;
  padding: 0;
  color: var(--ink);
}

.empty-hint {
  font-size: 12px;
  opacity: 0.5;
  font-style: italic;
}

/* ── Repeater cards ──────────────────────────────────────────────────── */
.repeater-card {
  border: var(--border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fafafa;
}

.repeater-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.remove-btn {
  background: none;
  border: 1px solid #ccc;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  color: #666;
  transition: color 0.15s, border-color 0.15s;
}
.remove-btn:hover { color: var(--ink); border-color: var(--ink); }

.add-entry-btn {
  border: 2px dashed var(--ink);
  background: transparent;
  padding: 12px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  width: 100%;
  color: var(--ink);
  transition: background 0.15s;
}
.add-entry-btn:hover { background: #f5f5f5; }

/* ── Generate Resume ─────────────────────────────────────────────────── */
.generate-btn {
  width: 100%;
  padding: 16px;
  background: var(--ink);
  color: var(--surface);
  border: var(--border);
  box-shadow: var(--shadow);
  font-weight: 900;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}
.generate-btn:hover:not(:disabled) { background: #222; }
.generate-btn:active:not(:disabled) { box-shadow: 1px 1px 0 var(--ink); transform: translate(3px,3px); }
.generate-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.generate-note {
  font-size: 11px;
  opacity: 0.5;
  text-align: center;
  font-style: italic;
}

/* ── Responsive ──────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .hero { flex-direction: column; }
  .topbar { padding: 12px 16px; }
  .content { padding: 16px 12px 40px; }
}
</style>
