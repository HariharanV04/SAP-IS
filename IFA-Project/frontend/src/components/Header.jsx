import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import logo from '@assets/logo.svg';
import { Button, Dropdown, DropdownItem, DropdownMenu, DropdownTrigger, User } from "@heroui/react";
import { Cancel01Icon, Menu02Icon } from 'hugeicons-react';
import { useAuthActions } from '@/features/auth/authUtils';
import { useSelector } from 'react-redux';

function Header({ isExpanded, toggleSidebar }) {
    const { handleLogout } = useAuthActions();
    const user = useSelector((state) => state.auth.user);
    const navigate = useNavigate()
    return (
        <nav className="fixed top-0 z-50 w-full bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
            <div className="px-3 py-1 lg:px-5 lg:pl-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center justify-start rtl:justify-end">
                        <Button className='md:hidden me-2' isIconOnly variant="bordered" onClick={toggleSidebar}>
                            {isExpanded ? <Cancel01Icon /> : <Menu02Icon />}
                        </Button>
                        <Link to='/' className="flex ms-2 md:me-24">
                            <img src={logo} className="h-16 me-3" alt="Logo" />
                        </Link>
                    </div>
                    <div className="flex items-center">
                        <Dropdown placement="bottom-start">
                            <DropdownTrigger>
                                <User
                                    as="button"
                                    avatarProps={{
                                        isBordered: true,
                                        // src: "https://i.pravatar.cc/150?u=a042581f4e29026024d",
                                        // icon: <UserIcon />
                                    }}
                                    className="transition-transform"
                                    description={user?.email}
                                    name={`${user?.first_name} ${user?.last_name}`}
                                    classNames={{
                                        wrapper: 'md:inline-flex hidden'
                                    }}
                                />
                            </DropdownTrigger>
                            <DropdownMenu aria-label="User Actions" variant="flat">
                                <DropdownItem key="profile" className="h-14 gap-2">
                                    <p className="font-bold">Signed in as</p>
                                    <p className="font-bold">{user?.email}</p>
                                </DropdownItem>
                                <DropdownItem onClick={() => navigate('/profile')}>
                                    My Profile
                                </DropdownItem>
                                <DropdownItem onClick={handleLogout} key="logout" color="danger">
                                    Log Out
                                </DropdownItem>
                            </DropdownMenu>
                        </Dropdown>
                    </div>
                </div>
            </div>
        </nav>
    )
}

export default Header