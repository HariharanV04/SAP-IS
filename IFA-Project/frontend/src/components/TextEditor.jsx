import React from 'react';
import ReactQuill from 'react-quill';

function TextEditor({ setFieldValue, ...props }) {
    const Font = ReactQuill.Quill.import('formats/font');
    Font.whitelist = [
        'Arial',
        'sans-serif',
        'serif',
        'monospace',
        'Calibri',
        'times-new-roman',
        'tahoma'
    ]; // Add standard and custom fonts
    ReactQuill.Quill.register(Font, true);


    const Size = ReactQuill.Quill.import('attributors/style/size');
    Size.whitelist = ['10px', '12px', '14px', '16px', '18px', '20px', '24px', '30px', '36px'];
    ReactQuill.Quill.register(Size, true);


    const modules = {
        toolbar: [
            [{ font: Font.whitelist }], // Custom font family options
            // [{ header: '1' }, { header: '2' }, { font: [] }],
            // [{ size: [] }],
            ['bold', 'italic', 'underline', 'strike', 'blockquote'],
            [
                { list: 'ordered' },
                { list: 'bullet' },
                { indent: '-1' },
                { indent: '+1' },
            ],
            [{ 'size': Size.whitelist }],
            [{ align: [] }], // Add text alignment options
            ['link'],
            ['clean'], // Remove formatting button
        ],
    };
    const formats = [
        'header', 'font', 'size',
        'bold', 'italic', 'underline', 'strike', 'blockquote',
        'list', 'bullet', 'indent',
        'link', 'image', 'align', // Include text alignment in formats
    ];


    return (
        <div className='flex direction-column'>
            <ReactQuill
                modules={modules}
                formats={formats}
                theme="snow"
                value={props.value}
                onChange={(e) => {
                    setFieldValue(e)
                }}
            />
        </div>
    )
}

export default TextEditor


export function RenderTextEditor(props) {
    // return <div className='ql-editor' dangerouslySetInnerHTML={{ __html: props.value }} />
    return <ReactQuill readOnly={true} theme={"bubble"}  {...props} />
}