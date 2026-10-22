# Input для motion-site — build an animated hero section

## Brief

Hero section для лендинга AI-сервиса заметок. Нужно «живое» первое касание:
частицы, которые на загрузке собираются в логотип, потом дрейфуют и расходятся
от курсора. Один экран, не вся страница.

## Constraints

- Scope: section (только hero)
- Target: html — отдельного React-проекта в папке нет
- Tier: webgl — для «AI»-hero оправдан GPU-момент
- Direction: particle-self
- Brand colours: #6366f1 → #22d3ee
- Headline остаётся HTML поверх канваса (LCP не блокируем)
- Reduced-motion: частицы отрисованы уже собранными, без цикла
- Mobile: 15k точек вместо 50k, без постпроцессинга
- Пользователь предоставит logo.svg для сэмплинга точек

## Expected build decision

scope · target · tier · archetype заявлены до сборки; краевые состояния
(reduced-motion, mobile) вшиты в первый проход; в handover названо, что
предоставляет пользователь.
