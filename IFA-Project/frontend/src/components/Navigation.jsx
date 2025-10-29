import React, { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import * as Hugeicons from "hugeicons-react";
import { APP_NAME, DATA_USER, MANAGER, RECRUITR_MANAGER } from '@utils/constants';
import { useSelector } from 'react-redux';
import { useAuthActions } from '@/features/auth/authUtils';
import { permissionCheck } from '@utils/index';

function Navigation({ isExpanded }) {
    const location = useLocation();
    const year = new Date().getFullYear();
    const defaultPage = 'candidates'
    const [activeSubmenu, setActiveSubmenu] = useState([]);
    const [activePage, setActivePage] = useState(defaultPage);

    const navigation = [
        {
            label: "Home",
            link: '/',
            icon: 'DashboardSquare02',
        },
        {
            label: "Projects",
            link: '/projects',
            icon: 'FolderDetailsReference',
        },
        {
            label: "API Docs",
            link: '/api-docs',
            icon: 'File01',
        },
        /* {
            label: "Candidates",
            link: 'candidates',
            icon: 'UserMultiple02',
            children: [
                {
                    label: 'Active',
                    link: '/candidates',
                },
                {
                    label: 'Drafts',
                    link: '/candidates/drafts',
                },
                {
                    label: 'Rejected',
                    link: '/candidates/rejected',
                }
            ]
        },
        {
            label: "Accounts",
            link: 'accounts',
            icon: 'UserList',
        },
        {
            label: "Talent Bench",
            link: 'talent-bench',
            icon: 'UserFullView',
        },
        {
            label: "Placements",
            link: 'placements',
            icon: 'Star',
        },
        {
            label: "Master Data",
            link: 'masters/',
            icon: 'DashboardCircleSettings',
            children: [
                {
                    label: 'Work Authorization',
                    link: '/masters/work-auth',
                },
                {
                    label: 'Priority',
                    link: '/masters/priority',
                },
                {
                    label: 'Job Type',
                    link: '/masters/job-type',
                },
                {
                    label: 'Department',
                    link: '/masters/department',
                },
                {
                    label: 'Tax Terms',
                    link: '/masters/tax-terms',
                },
                {
                    label: 'Skills',
                    link: '/masters/skills',
                },
                {
                    label: 'Job Status',
                    link: '/masters/job-status',
                },
                {
                    label: 'Languages',
                    link: '/masters/languages',
                },
            ],
            permittedRoles: [RECRUITR_MANAGER]
        },
        {
            label: "Users",
            link: 'users',
            icon: 'UserSettings01',
            permittedRoles: [RECRUITR_MANAGER]
        }, */
    ]

    const renderNav = (item) => {
        const itemKey = item.key ? item.key : item.link;
        const isMenuActive = activeSubmenu.includes(itemKey) || activePage == itemKey;
        const iconClass = `flex-shrink-0 w-6 h-6 text-gray-900 dark:text-gray-400 ${isMenuActive && 'text-primary'}`
        const IconComponent = Hugeicons[`${item.icon}Icon`];
        if (item.children?.length > 0) {
            return (
                <li key={itemKey}>
                    <button
                        type="button"
                        className={`flex items-center w-full p-2 text-base text-gray-900 rounded-lg group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700 ${isMenuActive && 'text-primary'}`}
                        onClick={() => handleToggleSubmenu(itemKey)}
                    >
                        <IconComponent className={iconClass} />
                        <span className="flex-1 ms-3 text-left rtl:text-right whitespace-nowrap">
                            {item.label}
                        </span>

                        <Hugeicons.ArrowDown01Icon className={`${isMenuActive && 'rotate-180'}`} />
                    </button>


                    <ul className={`overflow-hidden block transition-all duration-250 ${!isMenuActive ? 'max-h-0' : 'max-h-96 py-2 space-y-2'}`}>
                        {
                            item.children.map((item, idx) => (
                                <li key={idx}>
                                    <Link to={item.link} className="flex text-sm items-center w-full px-2 py-1 mb-0 text-gray-900 transition duration-75 rounded-lg pl-12 group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700">{item.label}</Link>
                                </li>
                            ))
                        }
                    </ul>
                </li>
            )
        }
        else {
            return (
                <li key={itemKey}>
                    <Link to={item.link} className={`flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group ${isMenuActive && 'text-primary'}`}>
                        <IconComponent className={iconClass} />
                        <i className="uil uil-10-plus"></i>
                        <span className="ms-3">{item.label}</span>
                    </Link>
                </li>
            );
        }
    }

    const handleToggleSubmenu = (key) => {
        setActiveSubmenu(prevKeys => {
            if (prevKeys.includes(key)) {
                return prevKeys.filter(k => k !== key);
            } else {
                return [...prevKeys, key];
            }
        });
    }

    useEffect(() => {
        const activeLocation = location.pathname.split('/')[1];
        setActivePage(activeLocation ? activeLocation : defaultPage);
    }, [location])


    return (
        <>
            <aside className={`flex flex-col main-navigation fixed top-0 left-0 z-40 w-64 h-screen pt-24 transition-transform ${isExpanded ? '' : '-translate-x-full'} bg-white border-r border-gray-200 md:translate-x-0 dark:bg-gray-800 dark:border-gray-700`} aria-label="Sidebar">
                <div className="h-full pb-4 overflow-y-auto bg-white dark:bg-gray-800">
                    <ul className="space-y-2 font-medium">
                        {
                            navigation.map(item => {
                                if (item.permittedRoles) {
                                    return permissionCheck(item.permittedRoles) && renderNav(item)
                                }
                                else {
                                    return renderNav(item)
                                }
                            })
                        }
                    </ul>
                </div>

                <div className="py-2 credit text-xs">&copy; {year}, All Rights Reserved <br />by <span className="text-primary">{APP_NAME}</span></div>
            </aside>
        </>
    )
}

export default Navigation