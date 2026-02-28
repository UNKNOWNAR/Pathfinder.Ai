<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';

const router = useRouter();
const isSignUp = ref(false);
const showLoginPassword = ref(false);
const showSignupPassword = ref(false);

const loginData = reactive({ username_or_email: '', password: '' });
const signupData = reactive({ username: '', email: '', password: '', role: 'student' });

const handleLogin = async () => {
  try {
    const res = await api.post('/login', loginData);
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('role', res.data.role);
    localStorage.setItem('username', res.data.username);
    
    // Redirect based on role
    if (res.data.role === 'admin') {
      router.push('/admin');
    } else {
      router.push('/dashboard');
    }
  } catch (err) {
    alert(err.response?.data?.message || 'Login failed');
  }
};

const handleSignup = async () => {
  try {
    await api.post('/signup', signupData);
    alert('Account created! Please log in.');
    isSignUp.value = false;
  } catch (err) {
    alert(err.response?.data?.message || 'Signup failed');
  }
};
</script>

<template>
  <div class="wrapper">
    <div class="login-container">

      <!-- Toggle row -->
      <div class="toggle-row">
        <span :class="['side-label', { active: !isSignUp }]">Log in</span>
        <label class="switch-toggle">
          <input type="checkbox" v-model="isSignUp" class="toggle-input">
          <span class="slider"></span>
        </label>
        <span :class="['side-label', { active: isSignUp }]">Sign up</span>
      </div>

      <!-- Flip card -->
      <div class="flip-card__inner" :class="{ flipped: isSignUp }">
        <!-- Login face -->
        <div class="flip-card__front">
          <div class="title">Log in</div>
          <form class="flip-card__form" @submit.prevent="handleLogin">
            <input class="flip-card__input" v-model="loginData.username_or_email" placeholder="Email/Username" type="text" required />
            <div class="password-wrapper">
              <input class="flip-card__input" v-model="loginData.password" placeholder="Password" :type="showLoginPassword ? 'text' : 'password'" required />
              <label class="show-pass-switch" title="Show password">
                <input type="checkbox" class="pass-toggle" v-model="showLoginPassword" />
                <span class="pass-slider"></span>
              </label>
            </div>
            <button class="flip-card__btn" type="submit">Let's go!</button>
          </form>
        </div>
        <!-- Sign up face -->
        <div class="flip-card__back">
          <div class="title">Sign up</div>
          <form class="flip-card__form" @submit.prevent="handleSignup">
            <input class="flip-card__input" v-model="signupData.username" placeholder="Name" type="text" required />
            <input class="flip-card__input" v-model="signupData.email" placeholder="Email" type="email" required />
            <div class="password-wrapper">
              <input class="flip-card__input" v-model="signupData.password" placeholder="Password" :type="showSignupPassword ? 'text' : 'password'" required />
              <label class="show-pass-switch" title="Show password">
                <input type="checkbox" class="pass-toggle" v-model="showSignupPassword" />
                <span class="pass-slider"></span>
              </label>
            </div>
            <select class="flip-card__input" v-model="signupData.role">
              <option value="student">Student</option>
              <option value="company">Company</option>
            </select>
            <button class="flip-card__btn" type="submit">Confirm!</button>
          </form>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
:root {
  --input-focus: #2d8cf0;
  --font-color: #323232;
  --main-color: #323232;
  --bg-color: #fff;
}

.wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e0e0e0;
}

.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}

/* --- Toggle Row --- */
.toggle-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.side-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  transition: color 0.3s;
}

.side-label.active {
  color: #323232;
}

.switch-toggle {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 20px;
  cursor: pointer;
}

.toggle-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  inset: 0;
  border-radius: 5px;
  border: 2px solid #323232;
  box-shadow: 4px 4px #323232;
  background-color: #fff;
  transition: 0.3s;
}

.slider::before {
  content: '';
  position: absolute;
  height: 20px;
  width: 20px;
  border: 2px solid #323232;
  border-radius: 5px;
  left: -2px;
  bottom: 2px;
  background-color: #fff;
  box-shadow: 0 3px 0 #323232;
  transition: 0.3s;
  box-sizing: border-box;
}

.toggle-input:checked + .slider {
  background-color: #2d8cf0;
}

.toggle-input:checked + .slider::before {
  transform: translateX(30px);
}

/* --- Flip Card --- */
.flip-card__inner {
  width: 300px;
  height: 380px;
  position: relative;
  perspective: 1000px;
  transform-style: preserve-3d;
  transition: transform 0.8s;
}

.flip-card__inner.flipped {
  transform: rotateY(180deg);
}

.flip-card__front,
.flip-card__back {
  position: absolute;
  inset: 0;
  padding: 28px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  background: lightgrey;
  border-radius: 5px;
  border: 2px solid #323232;
  box-shadow: 4px 4px #323232;
  backface-visibility: hidden;
}

.flip-card__back {
  transform: rotateY(180deg);
}

.flip-card__form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  width: 100%;
}

.title {
  font-size: 25px;
  font-weight: 900;
  color: #323232;
}

.flip-card__input {
  width: 250px;
  height: 40px;
  border-radius: 5px;
  border: 2px solid #323232;
  background-color: #fff;
  box-shadow: 4px 4px #323232;
  font-size: 15px;
  font-weight: 600;
  padding: 5px 10px;
  outline: none;
  box-sizing: border-box;
}

.flip-card__btn {
  margin-top: 6px;
  width: 120px;
  height: 40px;
  border-radius: 5px;
  border: 2px solid #323232;
  background-color: #fff;
  box-shadow: 4px 4px #323232;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}

.flip-card__btn:active {
  box-shadow: 0px 0px #323232;
  transform: translate(3px, 3px);
}
/* --- Password Wrapper & Show-Password Toggle --- */
.password-wrapper {
  position: relative;
  width: 250px;
}

.password-wrapper .flip-card__input {
  width: 100%;
  padding-right: 62px;
  box-sizing: border-box;
}

.show-pass-switch {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  display: inline-block;
  width: 50px;
  height: 24px;
  cursor: pointer;
}

.pass-toggle {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.pass-slider {
  position: absolute;
  inset: 0;
  border-radius: 100px;
  border: 2px solid #323232;
  box-shadow: 2px 2px #323232;
  background-color: #ccc;
  transition: background-color 0.3s;
  box-sizing: border-box;
}

.pass-slider::before {
  content: "off";
  box-sizing: border-box;
  position: absolute;
  height: 18px;
  width: 18px;
  left: 1px;
  top: 1px;
  border: 2px solid #323232;
  border-radius: 100px;
  background-color: #fff;
  color: #323232;
  font-size: 7px;
  font-weight: 700;
  text-align: center;
  line-height: 14px;
  transition: transform 0.3s;
}

.pass-toggle:checked + .pass-slider {
  background-color: #2d8cf0;
}

.pass-toggle:checked + .pass-slider::before {
  content: "on";
  transform: translateX(26px);
}
</style>
