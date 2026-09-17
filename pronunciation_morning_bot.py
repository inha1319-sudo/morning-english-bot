import os
import sys
import json
import random
from datetime import datetime
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# 설정
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
CHATGPT_INSTRUCTION_FILE = SCRIPT_DIR / "ChatGPT발음지시문.md"

# 목표 표현 데이터 (기존 표현들 재사용)
EXPRESSIONS_DATA = [
    ("To be honest with you", "솔직히 말해서", "To be honest with you, I've never been a big fan of hiking."),
    ("As a matter of fact", "사실은", "As a matter of fact, I go to the coffee shop almost every single day."),
    ("Speaking of which", "말이 나와서 말인데", "Speaking of which, I've been to Daejeon."),
    ("Come to think of it", "생각해 보니", "Come to think of it, I haven't eaten anything all day."),
    ("What I'm trying to say is", "내 말의 요점은", "What I'm trying to say is that intonation is really important."),
    ("Long story short", "한마디로 줄이자면", "Long story short, I missed the last bus and had to walk home."),
    ("In a nutshell", "요약하자면", "In a nutshell, the project was a success."),
    ("On top of that", "게다가", "The hotel room was dirty and on top of that, the air conditioner was broken."),
    ("Last but not least", "마지막으로 중요한 건", "Last but not least, we need to consider the budget."),
    ("Don't get me wrong", "오해하지 마", "Don't get me wrong, studying vocabulary is good."),
    ("Strictly speaking", "엄격히 말하자면", "Strictly speaking, tomatoes are fruits, not vegetables."),
    ("It just crossed my mind", "방금 떠오른 건데", "A great idea just crossed my mind for our next project."),
    ("For the time being", "당분간은", "I'm staying at my parents' house for the time being."),
    ("In the meantime", "그 사이에", "In the meantime, I'm trying to record this video."),
    ("Contrary to expectation", "기대와 달리", "Contrary to expectation, the sequel was actually better."),
    ("Interestingly enough", "흥미롭게도", "Interestingly enough, I ran into my teacher at the concert."),
    ("Believe it or not", "믿거나 말거나", "Believe it or not, if you memorize scripts, you are likely to get NH."),
    ("You know what I mean?", "무슨 말인지 알지?", "You know what I mean? It's really frustrating."),
    ("Does that make sense?", "이해가 돼?", "Does that make sense?"),
    ("Let's put it this way", "이렇게 말해볼게", "Let's put it this way, if I buy this car, I'll be broke."),
    ("If I remember correctly", "내 기억이 맞다면", "If I remember correctly, the last time I visited Jeju was 5 years ago."),
    ("Correct me if I'm wrong", "내가 틀렸을 수도 있지만", "Correct me if I'm wrong, but didn't you subscribe to my channel?"),
    ("Honestly", "정직하게/솔직히", "Honestly, I don't know what to do."),
    ("Actually", "사실은", "Actually, I changed my mind."),
    ("Take a stroll", "산책하다", "I like to take a stroll along the river after dinner."),
    ("Jogging trail", "조깅 코스/산책로", "There is a well-maintained jogging trail in the park."),
    ("Fresh air", "신선한 공기", "I went outside to get some fresh air."),
    ("Greenery", "녹지/초록 식물", "Looking at the greenery helps me relax my eyes."),
    ("Bench", "벤치", "We sat on a bench and watched people passing by."),
    ("Fountain", "분수대", "Kids love playing in the water at the fountain."),
    ("Playground", "놀이터", "I used to play at the playground until the sunset when I was young."),
    ("Walk my dog", "개를 산책시키다", "My daily routine includes walking my dog in the morning."),
    ("Enjoy the breeze", "산들바람을 즐기다", "We sat by the river to enjoy the cool breeze."),
    ("Cherry blossoms", "벚꽃", "The park is famous for beautiful cherry blossoms in spring."),
    ("Foliage", "단풍", "The foliage in the mountain is breathtaking."),
    ("Picnic", "소풍", "We packed some sandwiches for a picnic."),
    ("Ride a bike", "자전거를 타다", "I learned how to ride a bike when I was seven."),
    ("Be on cloud nine", "기분이 날아갈 듯이 매우 좋을 때", "When I got the job offer, I was literally on cloud nine."),
    ("Over the moon", "세상을 다 가진 것처럼 기쁠 때", "My sister was over the moon when she found out she was pregnant."),
    ("Make one's day", "하루를 기분 좋게 만들었을 때", "Your subscription really made my day."),
    ("Feel blue", "우울하거나 기분이 처질 때", "I usually feel blue on rainy days."),
    ("Be burned out", "완전히 지치거나 방전되었을 때", "After working on the project for months without a break, I was completely burned out."),
    ("That's a bummer", "아쉽거나 실망스러울 때", "The concert was canceled due to heavy rain. It was such a bummer."),
    ("Let someone down", "누군가를 실망시켰을 때", "I don't wanna let my parents down."),
    ("Drive me crazy", "나를 미치게 만들 때", "You are driving me crazy."),
    ("Get on my nerves", "신경을 긁거나 거슬릴 때", "It really gets on my nerves when people talk loudly in the library."),
    ("Freak out", "기겁하거나 멘붕이 올 때", "I totally freaked out when I saw a huge cockroach in my room."),
    ("Blow off some steam", "화나 스트레스를 풀 때", "I usually go to the karaoke to blow off some steam."),
    ("Have butterflies in my stomach", "긴장되거나 설렐 때", "I always have butterflies in my stomach before a big presentation."),
    ("Be scared to death", "무서워 죽을 것 같을 때", "I was scared to death."),
    ("Chill out", "느긋하게 쉴 때", "On weekends I just want to stay home, watch Netflix, and chill out."),
    ("Recharge my battery", "재충전할 때", "My dog helps me recharge my battery."),
    ("Feel refreshed", "상쾌하고 개운할 때", "A walk in the park made me feel refreshed and energized."),
    ("Mixed feelings", "시원섭섭하거나 만감이 교차할 때", "I had mixed feelings about graduating from college."),
    ("Torn between A and B", "결정하기 힘들거나 고민될 때", "I was torn between buying a laptop and a tablet."),
    ("Second to none", "최고이거나 둘째가라면 서러울 때", "When it comes to fried chicken, Korea is second to none."),
    ("Out of this world", "환상적이거나 세상 맛이 아닐 때", "The steak at the restaurant was out of this world."),
    ("Breathtaking", "숨 막히게 아름다울 때", "The night view of Seoul from Namsan Tower is breathtaking."),
    ("Mind-blowing", "충격적으로 멋지거나 놀라울 때", "The special effects in the movie were absolutely mind-blowing."),
    ("Mediocre", "그저 그렇거나 2% 부족할 때", "Honestly, the food was mediocre."),
    ("Tedious", "지루하고 따분할 때", "The lecture was so tedious that I almost fell asleep."),
    ("Be hooked on", "~에 푹 빠지다/꽂히다", "Lately, I'm totally hooked on watching YouTube."),
    ("Be obsessed with", "~에 미치도록 좋아하다/집착하다", "My brother is obsessed with soccer."),
    ("Be into", "~에 관심이 있다/푹 빠져 있다", "I'm into movies these days."),
    ("Have a thing for", "~를 특별히 좋아하다/취향이다", "I have a thing for romantic comedies."),
    ("Be a big fan of", "~의 광팬이다", "I'm a big fan of Marvel movies."),
    ("Not my cup of tea", "내 취향이 아니다", "Horror movies are not my cup of tea."),
    ("It's not my thing", "내 스타일이 아니다", "It's not my thing. I hate bugs and sleeping outside."),
    ("Go-to place", "단골집/자주 가는 곳", "This cafe is my go-to place whenever I need to focus."),
    ("Regular haunt", "아지트/자주 출몰하는 곳", "That pub used to be my regular haunt back in college."),
    ("Kill time", "시간 때우기", "Playing mobile games is the best way to kill time on the subway."),
    ("Lose track of time", "시간 가는 줄 모르다", "It was so fun that I lost track of time while binge-watching them."),
    ("Spend quality time", "오붓하고 알찬 시간 보내기", "I spend quality time with my family on weekends."),
    ("Vibe", "분위기/느낌", "I really like the vibe of the restaurant."),
    ("Cozy atmosphere", "아늑한 분위기", "The cafe has a warm and cozy atmosphere."),
    ("Hustle and bustle", "도시의 북적거림/활기참", "I enjoy the hustle and bustle of the traditional market."),
    ("Hidden gem", "숨겨진 명소", "I found a small bakery which is a hidden gem in my neighborhood."),
    ("Hot spot", "핫플레이스/인기 있는 곳", "Gangnam is a hot spot for nightlife in Seoul."),
    ("A must-visit", "꼭 가봐야 할 곳", "If you go to Paris, the Eiffel Tower is a must-visit."),
    ("Tourist trap", "바가지 씌우는 관광지", "That market is a total tourist trap."),
    ("Rip-off", "바가지/너무 비싼 것", "$15 for a coffee? That's a rip-off."),
    ("Bang for the buck", "가성비 최고", "This laptop offers the best bang for the buck."),
    ("Reasonable price", "합리적인 가격", "The food was delicious and served at a reasonable price."),
    ("User-friendly", "사용하기 편한", "The app is very user-friendly."),
    ("State-of-the-art", "최첨단의", "The AI technology is state-of-the-art."),
    ("Game changer", "판도를 바꾸는 것/혁신", "Nowadays, AI is a game changer."),
    ("Be a creature of habit", "늘 하던 대로 하는 사람", "I'm a creature of habit so I always order the same coffee every morning."),
    ("Morning person", "아침형 인간", "I'm definitely not a morning person."),
    ("Night owl", "올빼미족", "I'm a night owl. I focus better at late at night when it's quiet."),
    ("Have a hectic schedule", "눈코 뜰 새 없이 바쁜 일정", "I have a hectic schedule this week."),
    ("Be packed with", "스케줄이 꽉 찬/붐비는", "My day is packed with meetings from 9 to 6."),
    ("Squeeze in", "짬을 내서 ~하다", "I try to squeeze in workout during my lunch break."),
    ("Procrastinate", "할 일을 미루다/늑장 부리다", "I always procrastinate."),
    ("Pull an all-nighter", "밤을 새우다", "I had to pull an all-nighter to finish the report on time."),
    ("Burn the midnight oil", "밤늦게까지 공부/일하다", "Students are burning the midnight oil for the final exams."),
    ("Cram for an exam", "벼락치기 하다", "I spent all night cramming for the history exam."),
    ("Pass with flying colors", "우수한 성적으로 통과하다", "You will pass the interview with flying colors."),
    ("Slacker", "게으름뱅이/농땡이", "He is such a slacker."),
    ("Couch potato", "소파와 한 몸이 되어 TV만 보는 사람", "On Sundays I turn into a couch potato and watch Netflix all day."),
    ("Lead a sedentary lifestyle", "주로 앉아서 생활하다", "More people have a sedentary lifestyle which is bad for health."),
    ("Get back in shape", "몸을 다시 만들다/건강을 되찾다", "I joined the gym to get back in shape before summer comes."),
    ("Work out", "운동하다", "I try to work out at least three times a week to stay healthy."),
    ("Eat a balanced diet", "균형 잡힌 식사를 하다", "It's important to maintain a balanced diet for your health."),
    ("Call in sick", "아파서 결근/병가 내다", "I felt terrible this morning, so I called in sick."),
    ("Feel under the weather", "컨디션이 안 좋은", "I'm feeling a bit under the weather today."),
    ("Come down with the flu", "감기/독감 기운이 있다", "I think I'm coming down with the flu."),
    ("Recover from", "~로부터 회복하다", "It took a week to fully recover from the surgery."),
    ("Keep up with", "~을 따라잡다/유행을 쫓다", "Fashion trends, they change so fast. So hard to keep up with."),
    ("Fall behind", "뒤처지다", "If you skip classes, you will fall behind quickly."),
    ("Struggle with", "고생하다/애먹다", "I'm currently struggling with back pain from sitting too long."),
    ("Get the hang of it", "요령을 터득하다/감을 잡다", "Driving was hard at first, but now I'm getting the hang of it."),
    ("Down to earth", "털털하고 현실적인, 허세가 없는 성격", "Despite being a famous celebrity, she is very down to earth."),
    ("Easy-going", "느긋하고 성격이 좋은, 까탈스럽지 않은", "My boss is pretty easy-going about deadlines."),
    ("Outgoing", "외향적이고 사교적인", "My sister is very outgoing and loves meeting new people."),
    ("Extroverted", "외향적이고 사교적인", "My sister is very outgoing and loves meeting new people."),
    ("Introverted", "내향적이고 내성적인", "I'm quite introverted, so I don't really like crowded places."),
    ("Life of the party", "분위기 메이커", "He is always the life of the party; he makes everyone laugh."),
    ("Party pooper", "분위기를 망치는 사람", "Don't be a party pooper; come and have fun."),
    ("People person", "사람을 좋아하고 사교적인 사람", "You need to be a people person to work in sales."),
    ("Short-tempered", "다혈질인, 성격이 급한", "My boss is so short-tempered."),
    ("Picky", "까탈스러운, 편식이 심한", "I am such a picky eater and I do not eat any non-Korean food."),
    ("Picky eater", "편식이 심한 사람", "I am such a picky eater and I do not eat any non-Korean food."),
    ("Close-knit", "사이가 끈끈하고 가까운", "I grew up in a very close-knit family."),
    ("Drift apart", "사이가 멀어지다, 소원해지다", "We used to be best friends, but we drifted apart after high school."),
    ("Keep in touch", "연락하고 지내다", "Let's keep in touch after you move abroad."),
    ("Lose touch", "연락이 끊기다", "I regret losing touch with my college roommate."),
    ("Bump into", "우연히 마주치다", "I bumped into my ex-boyfriend at the mall yesterday."),
    ("Hit it off", "죽이 잘 맞다, 금방 친해지다", "We hit it off immediately because we both love jazz."),
    ("See eye to eye", "의견이 일치하다", "My father and I don't see eye to eye on politics."),
    ("Have a falling out", "다투다, 사이가 틀어지다", "I had a falling out with my friend over money issues."),
    ("Make up", "화해하다", "We argued last night, but we made up this morning."),
    ("Look up to", "존경하다", "I've always looked up to my mother."),
    ("Take after", "성격 등을 닮다", "I take after my dad in personality."),
    ("Role model", "롤모델", "My English teacher is my role model."),
    ("Something came up", "갑자기 일이 생기다", "I'm sorry, but something came up at work."),
    ("Slipped my mind", "깜빡 잊어버리다", "I'm sorry, it completely slipped my mind."),
    ("My mind went blank", "머릿속이 하얘지다", "I was so nervous during the interview that my mind went blank."),
    ("On the tip of my tongue", "입가에서 맴돌다", "His name is on the tip of my tongue, but I can't remember."),
    ("Screw up", "망치다", "So I messed up the test."),
    ("Mess up", "망치다", "So I messed up the test."),
    ("Fix a problem", "문제를 해결하다", "I want to fix this problem."),
    ("Sort it out", "문제를 해결하다/정리하다", "I wanna sort it out."),
    ("Deal with", "다루다, 처리하다", "I have to deal with difficult customers every day."),
    ("Come up with", "아이디어를 생각해내다", "She came up with a brilliant idea for the marketing campaign."),
    ("Figure out", "이해하다, 알아내다", "I can't figure out how to use this new coffee machine."),
    ("Make it up to you", "미안한 마음을 보상하다/만회하다", "I wanna make it up to you."),
    ("Ask for a refund", "환불을 요청하다", "Can I ask for a refund if I lost a receipt?"),
    ("Exchange A for B", "A를 B로 교환하다", "I'd like to exchange this T-shirt for a large size."),
    ("Run out of", "~이 다 떨어지다/고갈되다", "We ran out of milk."),
    ("Out of order", "고장 난", "The elevator is out of order."),
    ("Second-hand", "중고의", "I bought a second-hand car to save money."),
    ("In stock", "재고가 있는", "I want to know if you have any red shirts in stock."),
    ("Out of stock", "품절된", "I want to know if you have any red shirts in stock."),
    ("Reschedule", "일정을 변경하다", "Can we reschedule the meeting to next week?"),
    ("Postpone", "미루다", "Let's postpone the meeting to next week."),
    ("At the last minute", "막판에, 마지막 순간에", "He always cancels at the last minute."),
    ("Give me a hand", "도와주다", "Can you give me a hand with these heavy boxes?"),
    ("Do me a favor", "부탁을 하나 들어주다", "Can you do me a favor?"),
    ("I was wondering if you could", "~해주실 수 있는지 궁금합니다", "I was wondering if you could help me with my homework."),
    ("Play a significant role", "중요한 역할을 하다", "Smartphone plays a significant role in our daily lives."),
    ("Have a major impact on", "~에 큰 영향을 미치다", "Global warming is having a major impact on the ecosystem."),
    ("Pros and cons", "장단점", "Living in a big city has pros and cons."),
    ("A double-edged sword", "양날의 검", "AI technology is a double-edged sword; it is helpful but threatens jobs."),
    ("Take something for granted", "~을 당연하게 여기다", "We often take our health for granted until we get sick."),
    ("Pay attention to", "~에 주의를 기울이다", "People are paying more attention to environmental issues these days."),
    ("Raise awareness", "경각심을 높이다", "We need to raise awareness of the dangers of drunk driving."),
    ("Eco-friendly", "친환경적인", "Electric cars are becoming popular because they are eco-friendly."),
    ("Advancement of technology", "기술의 발전", "Thanks to the advancement of technology, our lives are much better."),
    ("Cutting-edge", "최첨단의", "The technology is cutting-edge."),
    ("Information overload", "정보 과부하", "We live in an era of information overload."),
    ("Invade privacy", "사생활을 침해하다", "CCTV cameras help prevent crime but they can invade privacy."),
    ("Identity theft", "명의 도용", "Identity theft is a serious crime."),
    ("Convenient but dangerous", "편리하지만 위험한", "Mobile banking is convenient but dangerous if you lose your phone."),
    ("Global warming", "지구 온난화", "Global warming is affecting our planet."),
    ("Climate change", "기후 변화", "Climate change is a major concern."),
    ("Separate trash", "분리수거", "We need to separate trash for recycling."),
    ("Recycling", "재활용", "Recycling helps the environment."),
    ("Real estate market", "부동산 시장", "The real estate market is crazy and the house price skyrocketed."),
    ("Skyrocket", "가격 등이 폭등하다", "The real estate market is crazy and the house price skyrocketed."),
    ("Competitive society", "경쟁 사회", "Korea is a highly competitive society."),
    ("Freezing job market", "얼어붙은 취업 시장", "The job market is freezing cold right now."),
    ("Generation gap", "세대 차이", "I feel a generation gap when I talk to my parents about technology."),
    ("Make ends meet", "근근이 먹고살다/수지를 맞추다", "With the rising cost of living, it is hard to make ends meet."),
    ("Once in a blue moon", "가뭄에 콩 나듯이, 아주 가끔", "I go to the library once in a blue moon."),
    ("A piece of cake", "식은 죽 먹기, 아주 쉬운 일", "The exam was a piece of cake."),
    ("A walk in the park", "누워서 떡 먹기, 매우 쉬운 일", "Compared to my last job, this one is a walk in the park."),
    ("Cost an arm and a leg", "등골이 휠 정도로 비싸다", "Buying a house in Seoul costs an arm and a leg."),
    ("Break the bank", "파산할 정도로 비싸다, 큰돈이 들다", "You can travel abroad without breaking the bank if you plan."),
    ("Save for a rainy day", "만약을 위해 저축하다", "My mom always told me to save money for a rainy day."),
    ("Hit the books", "공부하다", "I have to hit the books."),
    ("Hit the sack", "자러 가다", "I'm going to hit the sack early tonight."),
    ("Call it a day", "오늘 일과를 마치다, 퇴근하다", "Let's call it a day and go home."),
    ("Ring a bell", "들어본 적 있다, 낯이 익다", "The name rings a bell but I can't remember his face."),
    ("Play by ear", "상황 봐서 하다, 임기응변하다", "Let's just play by ear."),
    ("Go with the flow", "대세를 따르다", "I just decided to go with the flow."),
    ("Sit on the fence", "결정을 못 내리고 관망하다", "Stop sitting on the fence and pick a side."),
    ("Cut to the chase", "본론으로 들어가다", "Let me just cut to the chase and tell you what happened."),
    ("Beat around the bush", "빙빙 돌려 말하다", "Stop beating around the bush and tell me what you want."),
    ("Spill the beans", "비밀을 누설하다", "Who spilled the beans about the surprise party?"),
    ("Let the cat out of the bag", "무심코 비밀을 말하다", "I accidentally let the cat out of the bag about her promotion."),
    ("Pull someone's leg", "놀리다, 농담하다", "Are you serious or are you pulling my leg?"),
    ("Break a leg", "공연 전 행운을 빌어", "Break a leg! You'll do great on stage!"),
    ("Under the radar", "눈에 띄지 않게 조용히", "I want to keep this project under the radar until finished."),
    ("Keep an eye on", "주시하다, 봐주다", "Can you keep an eye on my bag while I go to the restroom?"),
    ("Give it a shot", "한 번 시도해 보다", "I'll give it a shot."),
    ("Get used to", "~에 익숙해지다", "It took me a while to get used to the spicy food in Korea."),
    ("Take advantage of", "~을 잘 활용하다", "You should take the advantage of the free membership."),
    ("Look forward to", "~을 고대하다, 기대하다", "I'm looking forward to hearing some positive news from you."),
    ("End up", "결국 ~하게 되다", "We planned to go hiking but ended up watching a movie."),
    ("Used to", "~하곤 했다", "I used to be slim but I'm not slim anymore."),
    ("Be supposed to", "~하기로 되어 있다", "The train was supposed to arrive at 9, but it's late."),
    ("Be likely to", "~할 것 같다", "It is likely to rain this afternoon."),
    ("Have no choice but to", "~할 수밖에 없다", "I had no choice but to take a taxi."),
    ("Can't help", "~하지 않을 수 없다", "The baby was so cute that I couldn't help smiling."),
    ("Renovate", "리노베이트 - 소규모 개조", "We're going to renovate the house next year."),
    ("Remodel", "리모델 - 큰 규모의 개조", "They decided to remodel the kitchen."),
    ("Spacious", "넓은", "The apartment is very spacious and bright."),
    ("Roomy", "넓은", "The car has a roomy interior."),
    ("Cramped", "매우 좁고 답답한", "My previous studio was so cramped that I could barely move."),
    ("Well-ventilated", "환기가 잘 되는", "It has a large window, so the room is well-ventilated."),
    ("Studio apartment", "원룸", "I rented a studio apartment in the city."),
    ("Fully furnished", "가구가 모두 갖춰진", "Is the room fully furnished?"),
    ("Amenities", "편의 시설", "The apartment complex has great amenities including a gym and a library."),
    ("Within walking distance", "걸어서 갈 수 있는 거리", "The gym is within walking distance."),
    ("Residential area", "주거 지역", "This is a quiet residential area."),
    ("Soundproof", "방음이 되는", "The walls are not soundproof, so I can hear everything."),
    ("Waterproof", "방수가 되는", "The bag is waterproof so your stuff won't get wet."),
    ("Monthly rent", "월세", "The monthly rent is expensive in this area."),
    ("Landlord", "집주인", "My landlord is very kind and helpful."),
    ("Lease contract", "임대 계약서", "I signed a lease contract for one year."),
    ("Move in", "이사 들어오다", "I'm moving in next week."),
    ("Move out", "이사 나가다", "I have to move out by the end of the month."),
    ("Utility bills", "공과금", "Utility bills are getting higher these days."),
    ("Maintenance fee", "관리비", "The maintenance fee is included in the rent."),
    ("Floor noise", "층간 소음", "There's too much floor noise from upstairs."),
    ("Housework", "집안일", "I try to split the housework with my brother."),
    ("Chores", "집안일", "I have to do my chores every day."),
    ("Mop the floor", "바닥을 대걸레질하다", "I just have to mop the floor."),
    ("Vacuum the floor", "청소기를 돌리다", "I need to vacuum the floor this weekend."),
    ("Air out the room", "환기하다", "Open the windows to air out the room."),
    ("Dust off", "먼지를 털다", "I need to dust off the bookshelves."),
    ("Declutter", "잡동사니를 정리하다/처분하다", "I decided to declutter my room."),
    ("Messy", "지저분한", "Sorry, my room is a little bit messy right now."),
    ("Spotless", "티끌 하나 없이 깨끗한", "My mom keeps the house spotless."),
    ("Mold", "곰팡이", "There's mold in the bathroom."),
    ("Leak", "물이 새다", "The ceiling is leaking; I need to call a plumber."),
    ("All-time favorite", "역대 최고로 좋아하는", "Inception is my all-time favorite movie."),
    ("Plot", "줄거리", "The plot was a bit confusing, but the action was great."),
    ("Storyline", "줄거리", "The plot was a bit confusing, but the action was great."),
    ("Plot twist", "(줄거리가 꼬인) 반전", "What I like about the movie was that it had a really crazy plot twist."),
    ("Spoiler", "스포일러 (내용 유출)", "I hate spoilers. They ruin the fun."),
    ("Cinematography", "영상미, 촬영 기법", "The cinematography was breathtaking."),
    ("Cast", "출연진", "The movie has a star-studded cast."),
    ("Director", "감독", "The director made a great film."),
    ("Genre", "장르", "What is your favorite movie genre? Action or romance?"),
    ("Action-packed", "액션이 가득한", "If you like action-packed movies, you should watch Mission Impossible."),
    ("Tear-jerker", "눈물을 쏙 빼놓는 영화/노래", "The movie is a total tear-jerker."),
    ("Thought-provoking", "시사하는 바가 큰, 생각하게 만드는", "It was a thought-provoking documentary about climate change."),
    ("Soundtrack", "사운드트랙", "I like the soundtrack."),
    ("Catchy", "귀에 맴도는, 중독성 있는", "It's catchy."),
    ("Upbeat", "경쾌한, 빠른 리듬의", "What I like about the movie music is that it has an upbeat rhythm."),
    ("Soothing", "마음을 진정시키는, 편안한", "Her voice is so soothing that it helps me sleep."),
    ("Lyrics", "가사", "The lyrics are very touching and relatable."),
    ("Touching", "감동적인", "The movie was very touching and emotional."),
    ("Relatable", "공감 가는", "The story was very relatable to people in their 20s."),
    ("Sing along", "따라 부르다, 떼창하다", "It was so fun to sing along with the crowd at the concert."),
    ("Live performance", "라이브 공연", "Their performance is even better than the recording."),
    ("Concert venue", "공연장", "The concert venue was packed with fans."),
    ("Packed with", "~로 꽉 찬", "The concert venue was packed with fans."),
    ("Atmosphere", "분위기", "The atmosphere at the stadium was absolutely electric."),
    ("Electric", "(분위기가) 열광적인, 짜릿한", "The atmosphere at the stadium was electric."),
    ("Goose bumps", "닭살, 소름", "His high notes gave me goose bumps."),
    ("Top-notch", "최고의, 일류의", "The service at the restaurant was top-notch."),
    ("Online shopping", "온라인 쇼핑", "I prefer online shopping because it's more convenient."),
    ("Browse the internet", "인터넷을 구경하다/둘러보다", "I try to browse the internet until I find the one that I like."),
    ("Add to the cart", "장바구니에 담다", "I add to my cart and then finally I just place an order."),
    ("Place an order", "주문하다", "Finally, I just place an order."),
    ("Delivery service", "배송 서비스", "I get delivery service."),
    ("Rocket delivery", "로켓 배송", "Thanks to rocket delivery, I received the package the next morning."),
    ("Try on", "(옷 등을) 입어보다", "Sometimes I don't like it because I can't try it on."),
    ("Fit perfectly", "딱 맞다", "I can try to find the clothes that fit perfectly."),
    ("Too tight", "너무 꽉 끼는", "Sometimes if they are too tight or too loose, I just don't need to buy."),
    ("Too loose", "너무 헐렁한", "Sometimes if they are too tight or too loose, I just don't need to buy."),
    ("Fashion conscious", "패션에 민감한", "Teenagers are very fashion conscious these days."),
    ("Trendsetter", "유행을 선도하는 사람", "She's a trendsetter in the fashion industry."),
    ("Impulse buying", "충동구매", "I have a habit of impulse buying when I'm stressed."),
    ("Window shopping", "아이쇼핑", "We went window shopping at the department store."),
    ("Bargain", "흥정(한 물건), 득템", "This coat was a real bargain."),
    ("Steal", "거저 얻은 것", "This coat is a real steal for the price."),
    ("On sale", "세일 중인", "Is it on sale?"),
    ("For sale", "판매용인", "The house is for sale at a good price."),
    ("Buy one get one free", "1+1 행사", "The convenience store has a buy one get one free deal on ice cream."),
    ("BOGO", "Buy One Get One free 약자", "The store is having a BOGO deal this week."),
    ("Refund policy", "환불 정책", "Please check the refund policy before purchasing."),
    ("Receipt", "영수증", "Don't forget to keep your receipt for the warranty."),
    ("Customer service", "고객 서비스", "The customer service was excellent."),
    ("Grocery shopping", "장보기", "I try to buy items in bulk for grocery shopping."),
    ("In bulk", "대량으로", "I try to buy items in bulk."),
    ("Sold out", "매진된", "Sometimes when they are sold out, I can just order online."),
    ("Limited edition", "한정판", "I decided to buy the shoes which was a limited edition."),
    ("Brand name clothes", "유명 브랜드 옷", "She only wears brand name clothes."),
    ("Knock-off", "짝퉁/모조품", "Be careful not to buy knock-offs online."),
    ("Smartphone addiction", "스마트폰 중독", "Smartphone addiction is a serious problem among teenagers."),
    ("Glue to the screen", "화면에 눈을 떼지 못하는", "Everyone on the subway is glued to the screen of their phones."),
    ("Laggy", "렉 걸리는, 버벅거리는", "My phone is so old that it's laggy."),
    ("Frozen screen", "멈춘 화면", "My computer crashed and I'm staring at a frozen screen."),
    ("Reboot", "재부팅하다", "Have you tried rebooting your routers?"),
    ("Restart", "재시작하다", "Have you tried rebooting your routers?"),
    ("Battery life", "배터리 수명", "The battery life of this phone is amazing."),
    ("Portable charger", "보조 배터리", "Portable charger is a must-have item for heavy phone users."),
    ("Wireless earphones", "무선 이어폰", "Wireless earphones are convenient but easy to lose."),
    ("Noise cancelling", "소음 제거", "Noise cancelling headphones are great when studying in noisy places."),
    ("Social media", "소셜 미디어", "I use social media to keep up with my friends' lives."),
    ("Post", "게시하다/올리다", "I posted a photo of my lunch on Instagram."),
    ("Upload", "올리다", "How often do you upload videos to your channel?"),
    ("Leave a comment", "댓글을 남기다", "Don't forget to like and leave a comment below."),
    ("Viral", "화제가 된, 떡상한", "The dance cover became a viral video overnight."),
    ("Influencer", "인플루언서", "Influencers have a huge impact on marketing trends."),
    ("Subscribe", "구독하다", "Please subscribe for more updates."),
    ("Stream", "스트리밍하다", "I use Spotify to stream music."),
    ("Wi-Fi connection", "와이파이 연결", "The Wi-Fi connection is unstable."),
    ("Signal", "신호", "I can't hear you well because the signal is weak."),
    ("User interface", "사용자 환경/UI", "The new update has a cleaner user interface."),
    ("Security breach", "보안 침해", "We need to prevent security breaches."),
    ("Hack", "해킹하다", "It's scary how hackers can easily hack personal devices."),
]

def load_env():
    """Load environment variables from .env file"""
    if not ENV_FILE.exists():
        return

    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if value:
                    os.environ[key.strip()] = value.strip()

def get_telegram_credentials():
    """Get Telegram bot token and chat ID"""
    token = os.getenv('PRONUNCIATION_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        load_env()
        token = os.getenv('PRONUNCIATION_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        raise ValueError("PRONUNCIATION_BOT_TOKEN or TELEGRAM_CHAT_ID not found")

    return token, chat_id

def get_five_expressions():
    """Get 5 random expressions"""
    return random.sample(EXPRESSIONS_DATA, 5)

def read_chatgpt_instruction_template():
    """Read ChatGPT instruction template"""
    with open(CHATGPT_INSTRUCTION_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def fill_instruction_template(template, context):
    """Fill the instruction template with context"""
    result = template
    for key, value in context.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result

def escape_html(text):
    """Escape HTML special characters"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_message(expressions):
    """Create the message with expressions"""
    lines = []

    lines.append("<b>오늘의 발음 연습 표현 5개</b>")
    lines.append("")

    for i, (eng, kor, example) in enumerate(expressions, 1):
        lines.append(f"{i}. {escape_html(eng)}")
        lines.append(f"   뜻: {escape_html(kor)}")
        lines.append(f"   예: {escape_html(example)}")

    lines.append("")
    lines.append("<b>학습법:</b>")
    lines.append("1. 다음 메시지 상자 눌러 복사")
    lines.append("2. ChatGPT 새 대화에 붙여 넣고 전송")
    lines.append("3. Ready. 오면 start 보내고 음성 켜기")
    lines.append("4. 각 표현마다 여러 번 따라 말하기")
    lines.append("5. 끝나면 wrap up 보내기")
    lines.append("6. 나온 피드백을 복사해서 이 봇에게 보내기")

    return "\n".join(lines)

def send_telegram_message(token, chat_id, text, parse_mode="HTML"):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    chunks = []
    if len(text) > 4000 and "<code>" not in text:
        current_chunk = ""
        for line in text.split("\n"):
            if len(current_chunk) + len(line) + 1 > 4000:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.append(current_chunk)
    else:
        chunks = [text]

    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode
        }

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")

        if i < len(chunks) - 1:
            import time
            time.sleep(1)

def main():
    """Main function"""
    load_env()
    token, chat_id = get_telegram_credentials()

    # Select 5 random expressions
    expressions = get_five_expressions()

    # Create main message
    main_message = create_message(expressions)
    send_telegram_message(token, chat_id, main_message)

    # Create ChatGPT instruction message
    template = read_chatgpt_instruction_template()

    # Format expressions for template
    expr_lines = []
    for eng, kor, example in expressions:
        expr_lines.append(f"• {eng} = {kor}\n  예시: {example}")
    expr_text = "\n".join(expr_lines)

    context = {
        "내이름": "Me",
        "상대이름": "Your English Pronunciation Coach",
        "표현5개": expr_text
    }

    filled_instruction = fill_instruction_template(template, context)
    escaped = escape_html(filled_instruction)
    instruction_message = f"<pre><code>{escaped}</code></pre>"

    send_telegram_message(token, chat_id, instruction_message, "HTML")

    print(f"Sent pronunciation practice for {len(expressions)} expressions")

if __name__ == "__main__":
    main()
