import React from 'react';
import clsx from 'clsx';
import {useWindowSize} from '@docusaurus/theme-common';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import DocItemPaginator from '@theme/DocItem/Paginator';
import DocVersionBanner from '@theme/DocVersionBanner';
import DocVersionBadge from '@theme/DocVersionBadge';
import DocItemFooter from '@theme/DocItem/Footer';
import DocItemTOCMobile from '@theme/DocItem/TOC/Mobile';
import DocItemTOCDesktop from '@theme/DocItem/TOC/Desktop';
import DocItemContent from '@theme/DocItem/Content';
import DocBreadcrumbs from '@theme/DocBreadcrumbs';
import ContentVisibility from '@theme/ContentVisibility';
import TopologyCanvas from '@site/src/components/TopologyCanvas';
import styles from './styles.module.css';

/**
 * Decide if the toc should be rendered, on mobile or desktop viewports
 */
function useDocTOC() {
  const {frontMatter, toc} = useDoc();
  const windowSize = useWindowSize();
  const hidden = frontMatter.hide_table_of_contents;
  const canRender = !hidden; // Allow rendering even if toc.length is 0 for graph
  
  const mobile = canRender && toc.length > 0 ? <DocItemTOCMobile /> : undefined;
  
  const desktop =
    canRender && (windowSize === 'desktop' || windowSize === 'ssr') ? (
      <DocItemTOCDesktop />
    ) : undefined;
    
  return {
    hidden,
    mobile,
    desktop,
    windowSize,
  };
}

export default function DocItemLayout({children}) {
  const docTOC = useDocTOC();
  const {metadata} = useDoc();
  
  // Always show the right sidebar column on desktop to accommodate the persistent relationship graph
  const showRightSidebar = docTOC.windowSize === 'desktop' || docTOC.windowSize === 'ssr';

  return (
    <div className="row">
      <div className={clsx('col', showRightSidebar && styles.docItemCol)}>
        <ContentVisibility metadata={metadata} />
        <DocVersionBanner />
        <div className={styles.docItemContainer}>
          <article>
            <DocBreadcrumbs />
            <DocVersionBadge />
            {docTOC.mobile}
            <DocItemContent>{children}</DocItemContent>
            <DocItemFooter />
          </article>
          <DocItemPaginator />
        </div>
      </div>
      {showRightSidebar && (
        <div className="col col--3">
          {/* Always render the relationship graph on desktop right sidebar (TOP) */}
          <div style={{ marginBottom: (!docTOC.hidden && docTOC.desktop) ? '2rem' : '0' }}>
            <TopologyCanvas height={300} />
          </div>
          {/* Render the actual TOC if it's not hidden and has items */}
          {!docTOC.hidden && docTOC.desktop}
        </div>
      )}

    </div>
  );
}

