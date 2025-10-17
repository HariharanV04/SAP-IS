import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import "@styles/globals.css";
import "@styles/custom.scss";
import 'react-quill/dist/quill.snow.css';
import "react-datepicker/dist/react-datepicker.css";
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from '@/store';
import { MsalProvider } from "@azure/msal-react";
import { msalInstance } from "./msalConfig";

ReactDOM.createRoot(document.getElementById('root')).render(
    <>
        <MsalProvider instance={msalInstance}>
            <BrowserRouter>
                <Provider store={store}>
                    <App />
                </Provider>
            </BrowserRouter>
        </MsalProvider>
    </>,
)
