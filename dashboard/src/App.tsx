import { ThemeProvider } from '@mui/material/styles';
import theme from './theme/theme';  // Adjust the import based on where your theme file is located
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Dashboard />
    </ThemeProvider>
  );
}

export default App;
