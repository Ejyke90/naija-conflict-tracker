# Fix Login Form Text Visibility

## Why
Users cannot see the text they type in login and registration forms due to insufficient contrast. This is a critical usability issue that prevents users from successfully authenticating.

## What Changes
- Add `text-gray-900` CSS class to all input elements in login and register forms
- Ensure text color provides sufficient contrast for accessibility

## Problem Statement
Users report that text in login and sign-up form input fields appears too light, making it difficult or impossible to see what they are typing. This creates a poor user experience and potential accessibility issues.

## Proposed Solution
Add explicit dark text color classes to all input elements in the login and register forms to ensure text is clearly visible against the white form background.

## Impact Assessment
- **Scope:** Frontend only - login.tsx and register.tsx pages
- **Risk:** Low - CSS class addition only
- **Testing:** Visual verification that text is dark and readable
- **Backward Compatibility:** Fully compatible - no breaking changes

## Success Criteria
- Input field text appears dark (black or dark gray) on all devices and browsers
- Users can clearly see characters as they type
- No regression in form functionality
- Maintains existing styling and layout

## Implementation Notes
- Add `text-gray-900` class to input elements
- Ensure placeholder text remains appropriately styled
- Test on both light and dark mode (though forms use light theme)</content>
<parameter name="filePath">/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/openspec/changes/fix-login-form-text-visibility/proposal.md