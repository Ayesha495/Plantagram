# Debug Notes - Day 1

## Issue: Black screen on phone, lagging
**Date:** [Today's date]
**Status:** Not resolved - will fix tomorrow

### Symptoms:
- QR code scan works
- Screen goes black
- Phone starts lagging
- No touch response

### What we tried:
- Created (auth) folder with login/signup screens
- Updated app/index.tsx to redirect to login
- Installed Expo Router structure

### What to try tomorrow:
1. Test in web browser first (press 'w')
2. Check terminal for error messages
3. Clear cache: `npx expo start -c`
4. Fix routing conflict between (tabs) and (auth)
5. Check app/_layout.tsx configuration

### Notes:
- (tabs) folder exists from original template
- Might be route conflict
- Need to properly configure Stack navigation