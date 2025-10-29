import { Chip, Tooltip } from "@heroui/react";
import dayjs from "dayjs";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { DATE_FORMAT, DATETIME_FORMAT, JOB_ID_FORMAT, MANAGER } from "./constants";
import { useSelector } from "react-redux";

export function capitalize(str) {
    return typeof str == 'string' ? str.charAt(0).toUpperCase() + str.slice(1) : str;
}
export function timeAgo(date) {
    const ms = new Date().getTime() - new Date(date).getTime();
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const months = Math.floor(days / 30);
    const years = Math.floor(months / 12);

    if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`;
    if (months > 0) return `${months} month${months > 1 ? 's' : ''} ago`;
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hr${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
    return `${seconds} sec${seconds !== 1 ? 's' : ''} ago`;
}

export function convertCSVToIntArray(value) {
    const newArray = value !== '' ? value.split(',').map(item => parseInt(item)) : []
    return newArray
}

export function convertArrayToCSV(value) {
    const newArray = value !== '' ? value.join(', ') : ""
    return newArray
}

export function getStatusChip(name) {
    const props = {
        classNames: {
            base: 'ms-2',
            content: 'font-semibold'
        },
        variant: "dot",
        size: 'sm'
    }
    switch (name) {
        case 'Success':
        case 'Active':
            return <Chip color="success" {...props}>{name}</Chip>;
        case 'Draft':
            return <Chip color="warning" {...props}>Draft</Chip>;
        case 'Cancelled':
        case 'Rejected':
            return <Chip color="danger" {...props}>{name}</Chip>;
        default:
            return <Chip color="success" {...props}>Active</Chip>;
    }
}

export function bytesToSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)), 10);
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
}

export const phoneCode = (value) => {
    let newValue = "";

    if (value && value !== "") {
        newValue = '+' + value.split(' ')[0];
    }

    return newValue;
}

export function dateFormat(value) {
    return value ? dayjs(value).format(DATE_FORMAT) : ''
}

export function dateTimeFormat(value) {
    return value ? dayjs(value).format(DATETIME_FORMAT) : ''
}

export function jobIdFormat(value) {
    return value && JOB_ID_FORMAT + value
}

export function currencySymbol(value) {
    const symbols = {
        "INR": "₹",
        "USD": "$"
    };
    return symbols[value] || "₹";
}

export function generateColorFromName(name) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    let color = '#';
    for (let i = 0; i < 3; i++) {
        const value = (hash >> (i * 8)) & 0xFF;
        color += ('00' + value.toString(16)).substr(-2);
    }

    return color;
}

export function getInitials(fullName) {
    const nameArray = fullName.split(' ');
    const initials = nameArray.map(word => word.charAt(0).toUpperCase()).join('');
    return initials;
}

export function permissionCheck(role = []) {

    const user = useSelector((state) => state.auth.user);

    console.log({
        user,
        role
    })

    return [1, MANAGER, ...role].includes(user?.role_id)
}


export function TruncatedText({ children }) {
    return (
        <Tooltip content={children}>
            <div className="truncate">{children}</div>
        </Tooltip>
    )
}