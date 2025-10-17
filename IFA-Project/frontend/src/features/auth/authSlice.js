import { createSlice } from '@reduxjs/toolkit';
import { jwtDecode } from 'jwt-decode';

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    authToken: null,
    user: {
      role_id: null
    }
  },
  reducers: {
    setAuthToken: (state, action) => {
      state.authToken = action.payload;
      state.user = jwtDecode(action.payload)
    },
    clearAuthToken: (state) => {
      state.authToken = null;
      state.user = {}
    },
  },
});

export const { setAuthToken, clearAuthToken } = authSlice.actions;
export default authSlice.reducer;
