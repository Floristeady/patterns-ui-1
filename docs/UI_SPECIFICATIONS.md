# UI Design Specifications
## AI Model Benchmarking Tool Frontend

### **Typography**
- **Primary Font**: Inter
- **Fallback**: System fonts

### **Color Palette**
- **Background**: Very light gray, almost white, with subtle blue tint
- **Text Colors**: 
  - **Dark gray** (for good readability on light background)
  - White (only for buttons with dark background)
- **Buttons**: Dark gray background with white text
- **Overall Scheme**: Whites and grayscale with very subtle blue tone

### **Borders and Shapes**
- **Border radius**: 16px on all elements (slightly rounded)
- **Apply to**:
  - Input boxes
  - Buttons
  - Containers/cards

### **Spacing**
- **Philosophy**: Generous spacing, not cramped
- Provide sufficient space between elements
- Avoid crowded feeling

### **Visual Style**
- **Aesthetic**: Minimalist, simple, clean
- **Prohibited**:
  - Shadows (box-shadows)
  - Gradients
  - Complex decorative elements
- **Focus**: Clean and direct approach

### **Micro-interactions**
- **Hover effects**: Subtle on buttons and interactive elements
- **Placeholders**: With smooth transitions
- **States**: Minimalist color/opacity changes

### **Main Layout**
- **Top section**: Input box for UI description
- **Bottom section**: Detailed results table for each model

### **Model Selector**
- **Type**: Dropdown
- **Behavior**: 
  - All models selected by default
  - User can deselect unwanted ones
  - Allow individual selection/deselection

### **Results Table**
- **Style**: Modern and minimalist table
- **Characteristics**:
  - **No borders** (except for necessary separations)
  - **Good row heights** for visual breathing room
  - **No cards** - clean table format
  - Subtle separations between sections if needed

### **Iconography**
- **Minimalist and functional** icons
- **Visual states**:
  - **Pending**: Gray icon (waiting)
  - **Running**: Blue icon with spinner (processing)
  - **Success**: Green icon with checkmark (completed)
  - **Error**: Red icon with X (error)

### **Notifications**
- **Toast/notifications** for completed actions
- Minimalist style consistent with overall design
- Non-intrusive positioning

### **Responsiveness**
- **Primary target**: Desktop
- **Secondary**: Responsive web (but not priority)
- **Mobile**: Not important for now

### **Final Elements**
- Input with subtle placeholder
- Table without unnecessary lines/borders
- Functional and beautiful icons
- Subtle micro-interactions
- Notifications for user feedback
- Everything with generous spacing and minimalist aesthetic

## Implementation Notes

### Color Variables (suggested)
```css
:root {
  --bg-primary: #fafafa; /* Very light gray with blue tint */
  --text-primary: #2d3748; /* Dark gray */
  --text-secondary: #718096; /* Medium gray */
  --text-white: #ffffff;
  --button-bg: #4a5568; /* Dark gray */
  --accent-blue: #4299e1; /* Subtle blue */
  --success-green: #48bb78;
  --error-red: #f56565;
  --warning-yellow: #ed8936;
}
```

### Typography Scale
```css
/* Primary text sizes */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
```

### Spacing Scale
```css
/* Generous spacing system */
--space-1: 0.25rem;
--space-2: 0.5rem;
--space-3: 0.75rem;
--space-4: 1rem;
--space-6: 1.5rem;
--space-8: 2rem;
--space-12: 3rem;
--space-16: 4rem;
```
