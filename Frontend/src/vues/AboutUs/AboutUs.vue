<template>
<div class="goofy-container">
<!-- Floating bubbles -->
<div class="bubble bubble-1">🫧</div>
<div class="bubble bubble-2">🫧</div>
<div class="bubble bubble-3">🫧</div>
<div class="bubble bubble-4">🫧</div>

<!-- Header Section -->
<div class="header-section">
<h1 class="super-goofy-title bouncing">🍍 Welcome to NXTCG! 🍍</h1>
<h2 class="sub-title sparkle">A Pure Imagination Workspace 🎩🪄</h2>
<p class="subtitle-rainbow">Where magical meetings happen!</p>
</div>

<div class="content-wrapper">
<!-- Mission Section -->
<section class="mission-section wonka-section">
<div class="section-icon">🎫</div>
<h2 class="section-title wonka-title">🍫 Our Golden Ticket Mission 🍫</h2>
<p class="section-quote wonka-quote">"Come with me, and you'll be in a world of pure imagination..."</p>
<p class="section-content">A Magical Card Game built from MaGiCaL pEoPlE</p>
</section>

<!-- Team Section -->
<section class="team-section hogwarts-section">
<div class="section-icon">🧙‍♂️</div>
<h2 class="section-title hogwarts-title">⚡ The Order of the Developers ⚡</h2>
<p class="section-quote hogwarts-quote">"I solemnly swear we are up to good code..."</p>
<div class="team-grid">
<div 
v-for="member in team" 
:key="member.name" 
class="team-chip wizard-chip">
<span class="team-name">{{ member.name }}</span>
<span class="team-role">{{ member.role }}</span>
</div>
</div>
</section>

<!-- Contact & Copyright -->
<div class="bottom-sections">
<section class="contact-section spongebob-section">
<div class="section-icon">📞</div>
<h2 class="section-title spongebob-title">🍔 Contact Us 🍔</h2>
<p class="section-quote spongebob-quote">"Is mayonnaise an instrument? No, but email is!"</p>
<p class="section-content">{{ contactEmail }}</p>
</section>

<section class="copyright-section mixed-section">
<div class="section-icon">📜</div>
<h2 class="section-title mixed-title">📜 Legal Stuff 📜</h2>
<p class="section-quote mixed-quote">"Mischief Managed... but also copyrighted!"</p>
<p class="section-content small-text">{{ copyright }}</p>
</section>
</div>
</div>

<!-- Footer -->
<div class="footer-goofy">
<p class="footer-text bouncing">🍍 F.U.N. = Files, Users, Nodes! 🍍</p>
<p class="footer-subtext">✨ "After all this time?" "Always... coding." ✨</p>
<div class="emoji-parade">
<span class="emoji floating">🍍</span>
<span class="emoji floating">🍫</span>
<span class="emoji floating">⚡</span>
<span class="emoji floating">🪄</span>
<span class="emoji floating">🫧</span>
</div>
</div>
</div>
</template>

<script setup>
defineOptions({ name: 'AboutUs' })

const team = [
    { name: 'Claire Oliver', role: 'Clarifymaxxing' },
    { name: 'Christy Dunlap', role: 'Likes Goose' },
    { name: 'Ben Edens', role: 'THE CHOSEN ONE OF POWERPOINTS WHO WILL BRING BALANCE TO THE PRESENTATIONS' },
    { name: 'Jessalyn Heckel', role: 'Wrangler of Brainrot' },
    { name: 'Bryce McWhirter', role: 'Certified Unc' },
]

const missionStatement = 'At NxtTCG, we bring collectors and players together in a vibrant marketplace for trading cards. Our mission is to make buying, selling, and discovering cards easy, fair, and fun for everyone.'
const contactEmail = 'support@nxttcg.com'
const copyright = `© ${new Date().getFullYear()} NxtTCG. All rights reserved.`
</script>

<style scoped>
.goofy-container {
min-height: 100vh;
background: linear-gradient(270deg, #ff6b6b, #4ecdc4, #f9ca24, #a29bfe, #fd79a8);
background-size: 1000% 1000%;
animation: rainbow-bg 10s ease infinite;
padding: 40px 20px;
font-family: 'Comic Sans MS', cursive, sans-serif;
position: relative;
overflow-x: hidden;
}

@keyframes rainbow-bg {
0% { background-position: 0% 50%; }
50% { background-position: 100% 50%; }
100% { background-position: 0% 50%; }
}

/* Bubbles */
.bubble {
position: absolute;
width: 80px;
height: 80px;
background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8), rgba(100, 200, 255, 0.6));
border-radius: 50%;
border: 2px solid rgba(255, 255, 255, 0.6);
box-shadow: inset 0 20px 30px rgba(255, 255, 255, 0.5), 0 10px 20px rgba(0, 0, 0, 0.2);
animation: bubble-float 6s ease-in-out infinite;
z-index: 1;
font-size: 2rem;
display: flex;
align-items: center;
justify-content: center;
}

.bubble-1 { top: 10%; left: 5%; width: 100px; height: 100px; animation-duration: 7s; }
.bubble-2 { top: 20%; right: 10%; width: 60px; height: 60px; animation-duration: 5s; animation-delay: 1s; }
.bubble-3 { bottom: 25%; left: 15%; width: 80px; height: 80px; animation-duration: 8s; animation-delay: 2s; }
.bubble-4 { bottom: 15%; right: 8%; width: 70px; height: 70px; animation-duration: 6s; animation-delay: 0.5s; }

@keyframes bubble-float {
0%, 100% { transform: translateY(0) translateX(0) scale(1); opacity: 0.7; }
25% { transform: translateY(-30px) translateX(20px) scale(1.1); opacity: 0.9; }
50% { transform: translateY(-60px) translateX(-10px) scale(0.95); opacity: 1; }
75% { transform: translateY(-30px) translateX(15px) scale(1.05); opacity: 0.85; }
}

/* Header */
.header-section {
text-align: center;
margin-bottom: 50px;
padding: 20px;
position: relative;
z-index: 2;
}

.super-goofy-title {
font-size: 3.5rem;
font-weight: bold;
color: white;
text-shadow: 3px 3px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 0 0 20px rgba(255, 255, 0, 0.8);
margin-bottom: 15px;
}

.sub-title {
font-size: 2rem;
color: #ffe135;
text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
margin-bottom: 10px;
font-style: italic;
}

.subtitle-rainbow {
font-size: 1.5rem;
color: white;
text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}

.sparkle { animation: sparkle-anim 1.5s ease-in-out infinite; }
@keyframes sparkle-anim {
0%, 100% { opacity: 1; transform: scale(1); }
50% { opacity: 0.8; transform: scale(1.05); }
}

.bouncing { animation: bounce 2s ease-in-out infinite; }
@keyframes bounce {
0%, 100% { transform: translateY(0); }
50% { transform: translateY(-20px); }
}

/* Loading */
.loading-section {
text-align: center;
padding: 100px 0;
position: relative;
z-index: 2;
}

.loading-text {
font-size: 2rem;
color: white;
margin-top: 30px;
text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
}

.pulsing { animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse {
0%, 100% { opacity: 1; transform: scale(1); }
50% { opacity: 0.7; transform: scale(1.1); }
}

/* Content */
.content-wrapper {
max-width: 1400px;
margin: 0 auto;
padding: 20px;
display: flex;
flex-direction: column;
gap: 40px;
position: relative;
z-index: 2;
}

section {
background: rgba(255, 255, 255, 0.95);
border-radius: 30px;
padding: 40px;
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
transition: all 0.3s ease;
border: 5px solid;
}

section:hover {
transform: translateY(-5px);
box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

.section-icon { text-align: center; margin-bottom: 20px; }

.section-title {
font-size: 2.5rem;
font-weight: bold;
text-align: center;
margin-bottom: 15px;
line-height: 1.3;
}

.section-quote {
font-style: italic;
font-size: 1.2rem;
text-align: center;
padding: 15px 30px;
margin: 15px auto;
border-radius: 15px;
max-width: 800px;
}

.section-content {
font-size: 1.3rem;
line-height: 1.8;
color: #333;
text-align: center;
padding: 20px;
}

.small-text { font-size: 1.1rem; }

/* Wonka */
.wonka-section {
border-color: #8b4513;
background: linear-gradient(135deg, rgba(255, 228, 181, 0.95), rgba(255, 215, 0, 0.95));
}

.wonka-title {
color: #8b4513;
text-shadow: 2px 2px 4px rgba(255, 215, 0, 0.8);
}

.wonka-quote {
color: #8b4513;
background: rgba(255, 215, 0, 0.3);
border-left: 5px solid #daa520;
}

/* Hogwarts */
.hogwarts-section {
border-color: #740001;
background: linear-gradient(135deg, rgba(116, 0, 1, 0.15), rgba(255, 215, 0, 0.15), rgba(255, 255, 255, 0.95));
}

.hogwarts-title {
color: #740001;
text-shadow: 2px 2px 6px rgba(255, 215, 0, 0.8);
}

.hogwarts-quote {
color: #740001;
background: rgba(255, 215, 0, 0.2);
border-left: 5px solid #740001;
}

/* SpongeBob */
.spongebob-section {
border-color: #0099ff;
background: linear-gradient(135deg, rgba(255, 238, 153, 0.95), rgba(255, 204, 0, 0.95));
}

.spongebob-title {
color: #0099ff;
text-shadow: 2px 2px 4px rgba(255, 204, 0, 0.8);
}

.spongebob-quote {
color: #0099ff;
background: rgba(0, 153, 255, 0.2);
border-left: 5px solid #ffcc00;
}

/* Mixed */
.mixed-section {
border: 5px dashed #9b59b6;
background: linear-gradient(135deg, rgba(243, 156, 18, 0.2), rgba(142, 68, 173, 0.2), rgba(231, 76, 60, 0.2), rgba(255, 255, 255, 0.8));
background-size: 400% 400%;
animation: mixed-gradient 5s ease infinite;
}

.mixed-title {
background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #f9ca24, #a29bfe);
background-size: 300% 300%;
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
animation: rainbow-text 3s ease infinite;
}

.mixed-quote {
color: #9b59b6;
background: linear-gradient(90deg, rgba(243, 156, 18, 0.2), rgba(142, 68, 173, 0.2));
border-left: 5px solid #8e44ad;
}

@keyframes mixed-gradient {
0%, 100% { background-position: 0% 50%; }
50% { background-position: 100% 50%; }
}

@keyframes rainbow-text {
0%, 100% { background-position: 0% 50%; }
50% { background-position: 100% 50%; }
}

/* Team */
.team-grid {
display: flex;
flex-wrap: wrap;
gap: 15px;
justify-content: center;
padding: 20px 0;
}

.team-chip {
padding: 25px 20px !important;
font-size: 1.2rem !important;
background: linear-gradient(135deg, #9b59b6, #e74c3c) !important;
animation: wizard-pulse 2s ease-in-out infinite;
transition: all 0.3s ease;
}

.team-chip:hover { transform: scale(1.1) rotate(2deg); }

.team-name {
font-weight: bold;
margin-right: 8px;
}

.team-role {
font-style: italic;
opacity: 0.9;
}

@keyframes wizard-pulse {
0%, 100% { box-shadow: 0 0 15px rgba(155, 89, 182, 0.5); }
50% { box-shadow: 0 0 30px rgba(231, 76, 60, 0.8); }
}

/* Bottom Sections */
.bottom-sections {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
gap: 30px;
}

/* Animations */
.spinning { animation: spin 3s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.wiggling { animation: wiggle 1s ease-in-out infinite; }
@keyframes wiggle {
0%, 100% { transform: rotate(0deg); }
25% { transform: rotate(-10deg); }
75% { transform: rotate(10deg); }
}

.shaking { animation: shake 0.5s ease-in-out infinite; }
@keyframes shake {
0%, 100% { transform: translateX(0); }
25% { transform: translateX(-10px); }
75% { transform: translateX(10px); }
}

.rotating { animation: rotate-wobble 3s ease-in-out infinite; }
@keyframes rotate-wobble {
0%, 100% { transform: rotate(-5deg); }
50% { transform: rotate(5deg); }
}

.floating { animation: float 3s ease-in-out infinite; }
@keyframes float {
0%, 100% { transform: translateY(0px); }
50% { transform: translateY(-10px); }
}

.golden-ticket { animation: golden-glow 2s ease-in-out infinite; }
@keyframes golden-glow {
0%, 100% { filter: drop-shadow(0 0 8px #ffd700); }
50% { filter: drop-shadow(0 0 25px #ffed4e); }
}

/* Error */
.error-section {
text-align: center;
padding: 100px 0;
position: relative;
z-index: 2;
}

.error-text {
font-size: 2rem;
color: white;
margin-top: 30px;
text-shadow: 2px 2px 8px rgba(255, 0, 0, 0.8);
}

/* Footer */
.footer-goofy {
text-align: center;
margin-top: 80px;
padding: 40px 0;
position: relative;
z-index: 2;
}

.footer-text {
font-size: 1.8rem;
color: white;
text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
margin-bottom: 10px;
}

.footer-subtext {
font-size: 1.3rem;
color: #ffd700;
text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
font-style: italic;
margin-bottom: 30px;
}

.emoji-parade {
display: flex;
justify-content: center;
gap: 30px;
font-size: 3rem;
}

.emoji {
display: inline-block;
animation: emoji-dance 2s ease-in-out infinite;
}

.emoji:nth-child(1) { animation-delay: 0s; }
.emoji:nth-child(2) { animation-delay: 0.2s; }
.emoji:nth-child(3) { animation-delay: 0.4s; }
.emoji:nth-child(4) { animation-delay: 0.6s; }
.emoji:nth-child(5) { animation-delay: 0.8s; }

@keyframes emoji-dance {
0%, 100% { transform: translateY(0px) rotate(0deg); }
25% { transform: translateY(-15px) rotate(-10deg); }
75% { transform: translateY(-15px) rotate(10deg); }
}

/* Scrollbar */
.goofy-container::-webkit-scrollbar { width: 15px; }
.goofy-container::-webkit-scrollbar-track {
background: linear-gradient(180deg, #ff6b6b, #4ecdc4, #f9ca24);
}
.goofy-container::-webkit-scrollbar-thumb {
background: linear-gradient(180deg, #a29bfe, #fd79a8);
border-radius: 10px;
border: 2px solid white;
}

/* Responsive */
@media (max-width: 968px) {
.super-goofy-title { font-size: 2.5rem; }
.sub-title { font-size: 1.5rem; }
.subtitle-rainbow { font-size: 1.2rem; }
.section-title { font-size: 2rem; }
.section-content { font-size: 1.1rem; }
.bottom-sections { grid-template-columns: 1fr; }
.emoji-parade { font-size: 2rem; gap: 15px; }
section { padding: 30px 20px; }
}

@media (max-width: 600px) {
.super-goofy-title { font-size: 2rem; }
.sub-title { font-size: 1.2rem; }
.section-title { font-size: 1.6rem; }
.team-chip { font-size: 1rem !important; padding: 18px 15px !important; }
}
</style>
